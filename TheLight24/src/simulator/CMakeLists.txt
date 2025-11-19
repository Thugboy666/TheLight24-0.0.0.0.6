find_package(pybind11 REQUIRED)

pybind11_add_module(physics_core
    simulator.cpp
)

target_include_directories(physics_core
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
)
