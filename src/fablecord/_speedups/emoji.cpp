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
#include <cstddef>

namespace {

struct EmojiObject
{
    PyObject_HEAD
    PyObject *name;
    PyObject *id;
    PyObject *state;
    PyObject *url;
    PyObject *animated;
};

struct emoji_state
{
    PyObject *id;
    PyObject *name;
    PyObject *animated;
    PyObject *empty;
};

extern PyModuleDef module;

emoji_state *state_of(PyTypeObject *type)
{
    PyObject *module_object = PyType_GetModuleByDef(type, &module);

    return module_object == nullptr ? nullptr : static_cast<emoji_state *>(PyModule_GetState(module_object));
}

void emoji_dealloc(EmojiObject *self)
{
    PyTypeObject *type = Py_TYPE(self);

    PyObject_GC_UnTrack(self);
    Py_XDECREF(self->name);
    Py_XDECREF(self->id);
    Py_XDECREF(self->state);
    Py_XDECREF(self->url);
    Py_XDECREF(self->animated);
    type->tp_free(reinterpret_cast<PyObject *>(self));
    Py_DECREF(type);
}

int emoji_traverse(EmojiObject *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    Py_VISIT(self->name);
    Py_VISIT(self->id);
    Py_VISIT(self->state);
    Py_VISIT(self->url);
    Py_VISIT(self->animated);

    return 0;
}

int emoji_clear(EmojiObject *self)
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

PyObject *emoji_from_dict(PyObject *cls, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 2) {
        PyErr_SetString(PyExc_TypeError, "from_dict() takes exactly two arguments: state and data");
        return nullptr;
    }

    PyObject *data = args[1];
    if (!PyDict_Check(data)) {
        PyErr_SetString(PyExc_TypeError, "data must be a dict");
        return nullptr;
    }

    PyTypeObject *type = reinterpret_cast<PyTypeObject *>(cls);
    emoji_state *keys = state_of(type);
    if (keys == nullptr) {
        return nullptr;
    }

    EmojiObject *self = reinterpret_cast<EmojiObject *>(type->tp_alloc(type, 0));
    if (self == nullptr) {
        return nullptr;
    }

    PyObject *name = PyDict_GetItemWithError(data, keys->name);
    if (name == nullptr) {
        if (PyErr_Occurred()) {
            Py_DECREF(self);
            return nullptr;
        }
        name = keys->empty;
    } else if (name == Py_None) {
        name = keys->empty;
    }
    self->name = Py_NewRef(name);

    self->state = Py_NewRef(args[0]);

    PyObject *raw = PyDict_GetItemWithError(data, keys->id);
    if (raw == nullptr && PyErr_Occurred()) {
        Py_DECREF(self);
        return nullptr;
    }

    if (raw == nullptr || raw == Py_None) {
        self->id = Py_NewRef(Py_None);
        self->animated = Py_NewRef(Py_False);

        return reinterpret_cast<PyObject *>(self);
    }

    PyObject *number = PyNumber_Long(raw);
    if (number == nullptr) {
        Py_DECREF(self);
        return nullptr;
    }
    self->id = number;

    PyObject *animated = PyDict_GetItemWithError(data, keys->animated);
    if (animated == nullptr) {
        if (PyErr_Occurred()) {
            Py_DECREF(self);
            return nullptr;
        }

        self->animated = Py_NewRef(Py_False);

        return reinterpret_cast<PyObject *>(self);
    }

    int moves = PyObject_IsTrue(animated);
    if (moves < 0) {
        Py_DECREF(self);
        return nullptr;
    }
    self->animated = Py_NewRef(moves ? Py_True : Py_False);

    return reinterpret_cast<PyObject *>(self);
}

PyObject *emoji_richcompare(PyObject *left, PyObject *right, int op)
{
    if ((op != Py_EQ && op != Py_NE) || !PyObject_TypeCheck(right, Py_TYPE(left))) {
        Py_RETURN_NOTIMPLEMENTED;
    }

    EmojiObject *self = reinterpret_cast<EmojiObject *>(left);
    EmojiObject *other = reinterpret_cast<EmojiObject *>(right);
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
        return nullptr;
    }

    return PyBool_FromLong(op == Py_NE ? !equal : equal);
}

Py_hash_t emoji_hash(EmojiObject *self)
{
    if (self->id == Py_None) {
        return PyObject_Hash(self->name);
    }

    PyObject *shift = PyLong_FromLong(22);
    if (shift == nullptr) {
        return -1;
    }

    PyObject *shifted = PyNumber_Rshift(self->id, shift);
    if (shifted == nullptr) {
        Py_DECREF(shift);
        return -1;
    }

    Py_DECREF(shift);

    Py_hash_t result = PyObject_Hash(shifted);
    Py_DECREF(shifted);

    return result;
}

PyMemberDef emoji_members[] = {
    {"name", T_OBJECT_EX, offsetof(EmojiObject, name), 0, "The character of a standard emoji, or the name of a custom one."},
    {"id", T_OBJECT_EX, offsetof(EmojiObject, id), 0, "The ID of a custom emoji, None for a standard one."},
    {"animated", T_OBJECT_EX, offsetof(EmojiObject, animated), 0, "Whether a custom emoji moves."},
    {"_state", T_OBJECT_EX, offsetof(EmojiObject, state), 0, nullptr},
    {"_url", T_OBJECT_EX, offsetof(EmojiObject, url), 0, nullptr},
    {nullptr, 0, 0, 0, nullptr}
};

PyMethodDef emoji_methods[] = {
    {"from_dict", reinterpret_cast<PyCFunction>(reinterpret_cast<void (*)()>(emoji_from_dict)), METH_FASTCALL | METH_CLASS, from_dict_doc},
    {nullptr, nullptr, 0, nullptr}
};

PyDoc_STRVAR(emoji_doc,
"The fields of an emoji and the two operations that run on every one\n"
"of them, kept in C++. PartialEmoji builds the rest on top.");

PyType_Slot emoji_slots[] = {
    {Py_tp_doc, const_cast<char *>(emoji_doc)},
    {Py_tp_dealloc, reinterpret_cast<void *>(emoji_dealloc)},
    {Py_tp_traverse, reinterpret_cast<void *>(emoji_traverse)},
    {Py_tp_clear, reinterpret_cast<void *>(emoji_clear)},
    {Py_tp_richcompare, reinterpret_cast<void *>(emoji_richcompare)},
    {Py_tp_hash, reinterpret_cast<void *>(emoji_hash)},
    {Py_tp_methods, static_cast<void *>(emoji_methods)},
    {Py_tp_members, static_cast<void *>(emoji_members)},
    {Py_tp_new, reinterpret_cast<void *>(PyType_GenericNew)},
    {0, nullptr}
};

PyType_Spec emoji_spec = {
    "fablecord._speedups.emoji.EmojiBase",
    static_cast<int>(sizeof(EmojiObject)),
    0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE,
    emoji_slots
};

int emoji_exec(PyObject *module_object)
{
    emoji_state *keys = static_cast<emoji_state *>(PyModule_GetState(module_object));

    keys->id = PyUnicode_InternFromString("id");
    keys->name = PyUnicode_InternFromString("name");
    keys->animated = PyUnicode_InternFromString("animated");
    keys->empty = PyUnicode_InternFromString("");

    if (keys->id == nullptr || keys->name == nullptr || keys->animated == nullptr || keys->empty == nullptr) {
        return -1;
    }

    PyObject *type = PyType_FromModuleAndSpec(module_object, &emoji_spec, nullptr);
    if (type == nullptr) {
        return -1;
    }

    int added = PyModule_AddObjectRef(module_object, "EmojiBase", type);
    Py_DECREF(type);

    return added;
}

int emoji_module_traverse(PyObject *module_object, visitproc visit, void *arg)
{
    emoji_state *keys = static_cast<emoji_state *>(PyModule_GetState(module_object));

    Py_VISIT(keys->id);
    Py_VISIT(keys->name);
    Py_VISIT(keys->animated);
    Py_VISIT(keys->empty);

    return 0;
}

int emoji_module_clear(PyObject *module_object)
{
    emoji_state *keys = static_cast<emoji_state *>(PyModule_GetState(module_object));

    Py_CLEAR(keys->id);
    Py_CLEAR(keys->name);
    Py_CLEAR(keys->animated);
    Py_CLEAR(keys->empty);

    return 0;
}

void emoji_module_free(void *module_object)
{
    emoji_module_clear(static_cast<PyObject *>(module_object));
}

PyModuleDef_Slot slots[] = {
    {Py_mod_exec, reinterpret_cast<void *>(emoji_exec)},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, nullptr}
};

PyDoc_STRVAR(module_doc, "The C++ base of fablecord.partial_emoji, used when it could be built.");

PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "fablecord._speedups.emoji",
    module_doc,
    sizeof(emoji_state),
    nullptr,
    slots,
    emoji_module_traverse,
    emoji_module_clear,
    emoji_module_free
};

}

PyMODINIT_FUNC PyInit_emoji(void)
{
    return PyModuleDef_Init(&module);
}