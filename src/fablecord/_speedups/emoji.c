/*
The MIT License (MIT)

Copyright (c) 2026-present cqlsh

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
*/

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>

typedef struct {
    PyObject_HEAD
    PyObject *name;
    PyObject *id;
    PyObject *state;
    PyObject *url;
    PyObject *animated;
} EmojiObject;

typedef struct {
    PyObject *id;
    PyObject *name;
    PyObject *animated;
    PyObject *empty;
} emoji_state;

static PyModuleDef module;

static emoji_state *state_of(PyTypeObject *type)
{
    PyObject *module_object = PyType_GetModuleByDef(type, &module);

    return module_object == NULL ? NULL : (emoji_state *)PyModule_GetState(module_object);
}

static void emoji_dealloc(EmojiObject *self)
{
    PyTypeObject *type = Py_TYPE(self);

    PyObject_GC_UnTrack(self);
    Py_XDECREF(self->name);
    Py_XDECREF(self->id);
    Py_XDECREF(self->state);
    Py_XDECREF(self->url);
    Py_XDECREF(self->animated);
    type->tp_free((PyObject *)self);
    Py_DECREF(type);
}

static int emoji_traverse(EmojiObject *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    Py_VISIT(self->name);
    Py_VISIT(self->id);
    Py_VISIT(self->state);
    Py_VISIT(self->url);
    Py_VISIT(self->animated);

    return 0;
}

static int emoji_clear(EmojiObject *self)
{
    Py_CLEAR(self->name);
    Py_CLEAR(self->id);
    Py_CLEAR(self->state);
    Py_CLEAR(self->url);
    Py_CLEAR(self->animated);

    return 0;
}

PyDoc_STRVAR(from_dict_doc,
"from_dict(state, data, /)\n"
"--\n"
"\n"
"Builds one from the emoji of a payload, reading the name, the ID and\n"
"whether it moves straight out of the dictionary.");

static PyObject *emoji_from_dict(PyObject *cls, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 2) {
        PyErr_SetString(PyExc_TypeError, "from_dict() takes exactly two arguments: state and data");
        return NULL;
    }

    PyObject *data = args[1];
    if (!PyDict_Check(data)) {
        PyErr_SetString(PyExc_TypeError, "data must be a dict");
        return NULL;
    }

    PyTypeObject *type = (PyTypeObject *)cls;
    emoji_state *keys = state_of(type);
    if (keys == NULL) {
        return NULL;
    }

    EmojiObject *self = (EmojiObject *)type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }

    PyObject *name = PyDict_GetItemWithError(data, keys->name);
    if (name == NULL) {
        if (PyErr_Occurred()) {
            Py_DECREF(self);
            return NULL;
        }
        name = keys->empty;
    } else if (name == Py_None) {
        name = keys->empty;
    }
    self->name = Py_NewRef(name);

    self->state = Py_NewRef(args[0]);

    PyObject *raw = PyDict_GetItemWithError(data, keys->id);
    if (raw == NULL && PyErr_Occurred()) {
        Py_DECREF(self);
        return NULL;
    }

    if (raw == NULL || raw == Py_None) {
        self->id = Py_NewRef(Py_None);
        self->animated = Py_NewRef(Py_False);

        return (PyObject *)self;
    }

    PyObject *number = PyNumber_Long(raw);
    if (number == NULL) {
        Py_DECREF(self);
        return NULL;
    }
    self->id = number;

    PyObject *animated = PyDict_GetItemWithError(data, keys->animated);
    if (animated == NULL) {
        if (PyErr_Occurred()) {
            Py_DECREF(self);
            return NULL;
        }

        self->animated = Py_NewRef(Py_False);

        return (PyObject *)self;
    }

    int moves = PyObject_IsTrue(animated);
    if (moves < 0) {
        Py_DECREF(self);
        return NULL;
    }
    self->animated = Py_NewRef(moves ? Py_True : Py_False);

    return (PyObject *)self;
}

static PyObject *emoji_richcompare(PyObject *left, PyObject *right, int op)
{
    if ((op != Py_EQ && op != Py_NE) || !PyObject_TypeCheck(right, Py_TYPE(left))) {
        Py_RETURN_NOTIMPLEMENTED;
    }

    EmojiObject *self = (EmojiObject *)left;
    EmojiObject *other = (EmojiObject *)right;
    int equal;

    if (self->id == Py_None) {
        if (other->id != Py_None) {
            equal = 0;
        } else {
            equal = PyObject_RichCompareBool(self->name, other->name, Py_EQ);
        }
    } else {
        equal = PyObject_RichCompareBool(self->id, other->id, Py_EQ);
    }

    if (equal < 0) {
        return NULL;
    }

    return PyBool_FromLong(op == Py_NE ? !equal : equal);
}

static Py_hash_t emoji_hash(EmojiObject *self)
{
    if (self->id == Py_None) {
        return PyObject_Hash(self->name);
    }

    PyObject *shift = PyLong_FromLong(22);
    if (shift == NULL) {
        return -1;
    }

    PyObject *shifted = PyNumber_Rshift(self->id, shift);
    if (shifted == NULL) {
        Py_DECREF(shift);
        return -1;
    }

    Py_DECREF(shift);

    Py_hash_t result = PyObject_Hash(shifted);
    Py_DECREF(shifted);

    return result;
}

static PyMemberDef emoji_members[] = {
    {"name", T_OBJECT_EX, offsetof(EmojiObject, name), 0, "The character of a standard emoji, or the name of a custom one."},
    {"id", T_OBJECT_EX, offsetof(EmojiObject, id), 0, "The ID of a custom emoji, None for a standard one."},
    {"animated", T_OBJECT_EX, offsetof(EmojiObject, animated), 0, "Whether a custom emoji moves."},
    {"_state", T_OBJECT_EX, offsetof(EmojiObject, state), 0, NULL},
    {"_url", T_OBJECT_EX, offsetof(EmojiObject, url), 0, NULL},
    {NULL, 0, 0, 0, NULL}
};

static PyMethodDef emoji_methods[] = {
    {"from_dict", (PyCFunction)(void (*)(void))emoji_from_dict, METH_FASTCALL | METH_CLASS, from_dict_doc},
    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(emoji_doc,
"The fields of an emoji and the two operations that run on every one\n"
"of them, kept in C. PartialEmoji builds the rest on top.");

static PyType_Slot emoji_slots[] = {
    {Py_tp_doc, (void *)emoji_doc},
    {Py_tp_dealloc, emoji_dealloc},
    {Py_tp_traverse, emoji_traverse},
    {Py_tp_clear, emoji_clear},
    {Py_tp_richcompare, emoji_richcompare},
    {Py_tp_hash, emoji_hash},
    {Py_tp_methods, emoji_methods},
    {Py_tp_members, emoji_members},
    {Py_tp_new, PyType_GenericNew},
    {0, NULL}
};

static PyType_Spec emoji_spec = {
    .name = "fablecord._speedups.emoji.EmojiBase",
    .basicsize = sizeof(EmojiObject),
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE,
    .slots = emoji_slots
};

static int emoji_exec(PyObject *module_object)
{
    emoji_state *keys = (emoji_state *)PyModule_GetState(module_object);

    keys->id = PyUnicode_InternFromString("id");
    keys->name = PyUnicode_InternFromString("name");
    keys->animated = PyUnicode_InternFromString("animated");
    keys->empty = PyUnicode_InternFromString("");

    if (keys->id == NULL || keys->name == NULL || keys->animated == NULL || keys->empty == NULL) {
        return -1;
    }

    PyObject *type = PyType_FromModuleAndSpec(module_object, &emoji_spec, NULL);
    if (type == NULL) {
        return -1;
    }

    int added = PyModule_AddObjectRef(module_object, "EmojiBase", type);
    Py_DECREF(type);

    return added;
}

static int emoji_module_traverse(PyObject *module_object, visitproc visit, void *arg)
{
    emoji_state *keys = (emoji_state *)PyModule_GetState(module_object);

    Py_VISIT(keys->id);
    Py_VISIT(keys->name);
    Py_VISIT(keys->animated);
    Py_VISIT(keys->empty);

    return 0;
}

static int emoji_module_clear(PyObject *module_object)
{
    emoji_state *keys = (emoji_state *)PyModule_GetState(module_object);

    Py_CLEAR(keys->id);
    Py_CLEAR(keys->name);
    Py_CLEAR(keys->animated);
    Py_CLEAR(keys->empty);

    return 0;
}

static void emoji_module_free(void *module_object)
{
    emoji_module_clear((PyObject *)module_object);
}

static PyModuleDef_Slot slots[] = {
    {Py_mod_exec, emoji_exec},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, NULL}
};

PyDoc_STRVAR(module_doc, "The C base of fablecord.partial_emoji, used when it could be built.");

static PyModuleDef module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "fablecord._speedups.emoji",
    .m_doc = module_doc,
    .m_size = sizeof(emoji_state),
    .m_slots = slots,
    .m_traverse = emoji_module_traverse,
    .m_clear = emoji_module_clear,
    .m_free = emoji_module_free
};

PyMODINIT_FUNC PyInit_emoji(void)
{
    return PyModuleDef_Init(&module);
}