#include "simulator.hpp"
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;

PYBIND11_MODULE(physics_core, m) {
    py::class_<Entity>(m, "Entity")
        .def(py::init<std::string,double,double,double,double,double>(),
             py::arg("name"), py::arg("x"), py::arg("y"), py::arg("mass"),
             py::arg("charge")=0.0, py::arg("spin")=0.0)
        .def_readwrite("x", &Entity::x)
        .def_readwrite("y", &Entity::y)
        .def_readwrite("vx", &Entity::vx)
        .def_readwrite("vy", &Entity::vy)
        .def_readwrite("mass", &Entity::mass)
        .def_readwrite("charge", &Entity::charge)
        .def_readwrite("spin", &Entity::spin)
        .def("repr", &Entity::repr);

    py::class_<Simulator>(m, "Simulator")
        .def(py::init<>())
        .def("add", &Simulator::add)
        .def("step", &Simulator::step)
        .def("snapshot", &Simulator::snapshot)
        .def_readwrite("dt", &Simulator::dt)
        .def_readwrite("area", &Simulator::area);
}
