#pragma once
#include <string>
#include <cmath>
#include <sstream>

struct Entity {
    std::string name;
    double x, y;
    double vx, vy;
    double mass;
    double charge;
    double spin;
    double radius;

    Entity(std::string n, double px, double py, double m, double q=0.0, double s=0.0)
        : name(std::move(n)), x(px), y(py), vx(0.0), vy(0.0),
          mass(m), charge(q), spin(s), radius(std::cbrt(m)*0.1) {}

    std::string repr() const {
        std::ostringstream ss;
        ss << "Entity(" << name << ", m=" << mass << ", q=" << charge << ")";
        return ss.str();
    }
};
