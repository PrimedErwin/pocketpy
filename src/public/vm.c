#include "pocketpy/objects/sourcedata.h"
#include "pocketpy/pocketpy.h"

#include "pocketpy/common/utils.h"
#include "pocketpy/common/sstream.h"
#include "pocketpy/objects/object.h"
#include "pocketpy/interpreter/vm.h"
#include "pocketpy/compiler/compiler.h"

pk_VM* pk_current_vm;
static pk_VM pk_default_vm;

void py_initialize() {
    pk_MemoryPools__initialize();
    py_Name__initialize();
    pk_current_vm = &pk_default_vm;
    pk_VM__ctor(&pk_default_vm);
}

void py_finalize() {
    pk_VM__dtor(&pk_default_vm);
    pk_current_vm = NULL;
    py_Name__finalize();
    pk_MemoryPools__finalize();
}

static void disassemble(CodeObject* co) {
    const static char* OP_NAMES[] = {
#define OPCODE(name) #name,
#include "pocketpy/xmacros/opcodes.h"
#undef OPCODE
    };

    c11_vector /*T=int*/ jumpTargets;
    c11_vector__ctor(&jumpTargets, sizeof(int));
    for(int i = 0; i < co->codes.count; i++) {
        Bytecode* bc = c11__at(Bytecode, &co->codes, i);
        if(Bytecode__is_forward_jump(bc)) {
            int target = (int16_t)bc->arg + i;
            c11_vector__push(int, &jumpTargets, target);
        }
    }

    c11_sbuf ss;
    c11_sbuf__ctor(&ss);

    int prev_line = -1;
    for(int i = 0; i < co->codes.count; i++) {
        Bytecode byte = c11__getitem(Bytecode, &co->codes, i);
        BytecodeEx ex = c11__getitem(BytecodeEx, &co->codes_ex, i);

        char line[8] = "";
        if(ex.lineno == prev_line) {
            // do nothing
        } else {
            snprintf(line, sizeof(line), "%d", ex.lineno);
            if(prev_line != -1) c11_sbuf__write_char(&ss, '\n');
            prev_line = ex.lineno;
        }

        char pointer[4] = "";
        c11__foreach(int, &jumpTargets, it) {
            if(*it == i) {
                snprintf(pointer, sizeof(pointer), "->");
                break;
            }
        }

        char buf[32];
        snprintf(buf, sizeof(buf), "%-8s%-3s%-3d ", line, pointer, i);
        c11_sbuf__write_cstr(&ss, buf);

        c11_sbuf__write_cstr(&ss, OP_NAMES[byte.op]);
        c11_sbuf__write_char(&ss, ex.is_virtual ? '*' : ' ');
        int padding = 24 - strlen(OP_NAMES[byte.op]);
        for(int j = 0; j < padding; j++) c11_sbuf__write_char(&ss, ' ');

        // _opcode_argstr(this, i, byte, co);
        do {
            if(Bytecode__is_forward_jump(&byte)) {
                c11_sbuf__write_int(&ss, (int16_t)byte.arg);
                c11_sbuf__write_cstr(&ss, " (to ");
                c11_sbuf__write_int(&ss, (int16_t)byte.arg + i);
                c11_sbuf__write_char(&ss, ')');
                break;
            }

            c11_sbuf__write_int(&ss, byte.arg);
            switch(byte.op) {
                case OP_LOAD_CONST:
                case OP_FORMAT_STRING:
                case OP_IMPORT_PATH: {
                    py_Ref tmp = c11__at(py_TValue, &co->consts, byte.arg);
                    c11_sbuf__write_cstr(&ss, " (");
                    // here we need to use py_repr, however this function is not ready yet
                    c11_sbuf__write_cstr(&ss, "<class '");
                    c11_sbuf__write_cstr(&ss, py_tpname(tmp->type));
                    c11_sbuf__write_cstr(&ss, "'>)");
                    break;
                }
                case OP_LOAD_NAME:
                case OP_LOAD_GLOBAL:
                case OP_LOAD_NONLOCAL:
                case OP_STORE_GLOBAL:
                case OP_LOAD_ATTR:
                case OP_LOAD_METHOD:
                case OP_STORE_ATTR:
                case OP_DELETE_ATTR:
                case OP_BEGIN_CLASS:
                case OP_GOTO:
                case OP_DELETE_GLOBAL:
                case OP_STORE_CLASS_ATTR:
                case OP_FOR_ITER_STORE_GLOBAL: {
                    c11_sbuf__write_cstr(&ss, " (");
                    c11_sbuf__write_cstr(&ss, py_name2str(byte.arg));
                    c11_sbuf__write_char(&ss, ')');
                    break;
                }
                case OP_LOAD_FAST:
                case OP_STORE_FAST:
                case OP_DELETE_FAST:
                case OP_FOR_ITER_STORE_FAST: {
                    py_Name name = c11__getitem(py_Name, &co->varnames, byte.arg);
                    c11_sbuf__write_cstr(&ss, " (");
                    c11_sbuf__write_cstr(&ss, py_name2str(name));
                    c11_sbuf__write_char(&ss, ')');
                    break;
                }
                case OP_LOAD_FUNCTION: {
                    const FuncDecl* decl = c11__getitem(FuncDecl*, &co->func_decls, byte.arg);
                    c11_sbuf__write_cstr(&ss, " (");
                    c11_sbuf__write_cstr(&ss, decl->code.name->data);
                    c11_sbuf__write_char(&ss, ')');
                    break;
                }
                case OP_BINARY_OP: {
                    py_Name name = byte.arg & 0xFF;
                    c11_sbuf__write_cstr(&ss, " (");
                    c11_sbuf__write_cstr(&ss, py_name2str(name));
                    c11_sbuf__write_char(&ss, ')');
                    break;
                }
            }
        } while(0);

        if(i != co->codes.count - 1) c11_sbuf__write_char(&ss, '\n');
    }

    c11_string* output = c11_sbuf__submit(&ss);
    pk_current_vm->_stdout("%s\n", output->data);
    c11_string__delete(output);
    c11_vector__dtor(&jumpTargets);
}

static bool
    pk_VM__exec(pk_VM* vm, const char* source, const char* filename, enum CompileMode mode) {
    CodeObject co;
    pk_SourceData_ src = pk_SourceData__rcnew(source, filename, mode, false);
    Error* err = pk_compile(src, &co);
    if(err) {
        PK_DECREF(src);
        return false;
    }

    disassemble(&co);

    Frame* frame = Frame__new(&co, &vm->main, NULL, vm->stack.sp, vm->stack.sp, &co);
    pk_VM__push_frame(vm, frame);
    pk_FrameResult res = pk_VM__run_top_frame(vm);
    CodeObject__dtor(&co);
    PK_DECREF(src);
    if(res == RES_ERROR) return false;
    if(res == RES_RETURN) return true;
    PK_UNREACHABLE();
}

bool py_exec(const char* source) { return pk_VM__exec(pk_current_vm, source, "<exec>", EXEC_MODE); }

bool py_eval(const char* source) { return pk_VM__exec(pk_current_vm, source, "<eval>", EVAL_MODE); }

bool py_call(py_Ref f, int argc, py_Ref argv) { return -1; }

bool py_callmethod(py_Ref self, py_Name name, int argc, py_Ref argv) { return -1; }

bool pk_vectorcall(int argc, int kwargc, bool op_call) { return -1; }

py_Ref py_retval() { return &pk_current_vm->last_retval; }

bool py_getunboundmethod(const py_Ref self,
                         py_Name name,
                         bool fallback,
                         py_Ref out,
                         py_Ref out_self) {
    return -1;
}

pk_TypeInfo* pk_tpinfo(const py_Ref self) {
    pk_VM* vm = pk_current_vm;
    return c11__at(pk_TypeInfo, &vm->types, self->type);
}

py_Ref py_tpfindmagic(py_Type t, py_Name name) {
    assert(py_ismagicname(name));
    pk_TypeInfo* types = (pk_TypeInfo*)pk_current_vm->types.data;
    do {
        py_Ref f = &types[t].magic[name];
        if(!py_isnull(f)) return f;
        t = types[t].base;
    } while(t);
    return NULL;
}

py_Ref py_tpmagic(py_Type type, py_Name name) {
    assert(py_ismagicname(name));
    pk_VM* vm = pk_current_vm;
    return &c11__at(pk_TypeInfo, &vm->types, type)->magic[name];
}

py_Ref py_tpobject(py_Type type) {
    pk_VM* vm = pk_current_vm;
    return &c11__at(pk_TypeInfo, &vm->types, type)->self;
}

const char* py_tpname(py_Type type) {
    pk_VM* vm = pk_current_vm;
    py_Name name = c11__at(pk_TypeInfo, &vm->types, type)->name;
    return py_name2str(name);
}

bool py_callmagic(py_Name name, int argc, py_Ref argv) {
    assert(argc >= 1);
    assert(py_ismagicname(name));
    py_Ref tmp = py_tpfindmagic(argv->type, name);
    if(!tmp) return TypeError(name);
    if(tmp->type == tp_nativefunc) return tmp->_cfunc(argc, argv);
    return py_call(tmp, argc, argv);
}
