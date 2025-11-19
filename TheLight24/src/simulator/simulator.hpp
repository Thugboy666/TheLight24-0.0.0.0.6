#pragma once
#include <vector>
#include <random>
#include "entity.hpp"
#include "physics.hpp"

class Simulator {
public:
    std::vector<Entity> entities;
    double dt = 1.0;
    double t = 0.0;
    double area = 10000.0;

    Simulator() = default;

    void add(const Entity &e) { entities.push_back(e); }

    void step(unsigned int steps=1) {
        for (unsigned int s=0; s<steps; ++s) {
            for (auto &a : entities) {
                double fx = 0.0, fy = 0.0;
                for (auto &b : entities) {
                    if (&a == &b) continue;
                    Physics::gravity(a,b,fx,fy);
                    Physics::coulomb(a,b,fx,fy);
                    Physics::yukawa(a,b,fx,fy);
                    Physics::casimir(a,b,fx,fy);
                }
                // aggiornamento velocità/posizione
                a.vx += (fx/a.mass)*dt;
                a.vy += (fy/a.mass)*dt;
                a.x += a.vx * dt;
                a.y += a.vy * dt;
                Physics::drag(a);
                // confini
                if (a.x < 0 || a.x > area) a.vx *= -0.9;
                if (a.y < 0 || a.y > area) a.vy *= -0.9;
            }
            t += dt;
        }
    }

    std::string snapshot() const {
        std::ostringstream ss;
        ss << "t=" << t << "  Entities=" << entities.size() << "\n";
        for (auto &e : entities) {
            ss << "  " << e.name << "  x=" << e.x << " y=" << e.y
               << " vx=" << e.vx << " vy=" << e.vy << "\n";
        }
        return ss.str();
    }
};
