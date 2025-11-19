#pragma once
#include <cmath>
#include "entity.hpp"

namespace Physics {

    constexpr double G = 6.67430e-11;   // gravitazionale
    constexpr double K = 8.9875517923e9; // coulomb
    constexpr double HBAR = 1.054571817e-34;

    // Calcolo forza gravitazionale tra due corpi
    inline void gravity(Entity &a, Entity &b, double &fx, double &fy) {
        double dx = b.x - a.x;
        double dy = b.y - a.y;
        double r2 = dx*dx + dy*dy + 1e-9;
        double f = G * a.mass * b.mass / r2;
        double invr = 1.0 / std::sqrt(r2);
        fx += f * dx * invr;
        fy += f * dy * invr;
    }

    // Forza di Coulomb
    inline void coulomb(Entity &a, Entity &b, double &fx, double &fy) {
        double dx = b.x - a.x;
        double dy = b.y - a.y;
        double r2 = dx*dx + dy*dy + 1e-9;
        double f = K * a.charge * b.charge / r2;
        double invr = 1.0 / std::sqrt(r2);
        fx += f * dx * invr;
        fy += f * dy * invr;
    }

    // Forza di Yukawa (campo mediato)
    inline void yukawa(Entity &a, Entity &b, double &fx, double &fy, double alpha=1e-10, double mu=1e-4) {
        double dx = b.x - a.x;
        double dy = b.y - a.y;
        double r = std::sqrt(dx*dx + dy*dy) + 1e-9;
        double f = alpha * std::exp(-mu*r) / (r*r);
        fx += f * dx / r;
        fy += f * dy / r;
    }

    // Forza Casimir semplificata (interazione quantica a corto raggio)
    inline void casimir(Entity &a, Entity &b, double &fx, double &fy) {
        double dx = b.x - a.x;
        double dy = b.y - a.y;
        double r = std::sqrt(dx*dx + dy*dy) + 1e-9;
        double f = -HBAR * 3.14159 / (240.0 * std::pow(r, 4));
        fx += f * dx / r;
        fy += f * dy / r;
    }

    // Attrito viscoso (simulazione fluido)
    inline void drag(Entity &a, double coeff=1e-5) {
        a.vx -= coeff * a.vx;
        a.vy -= coeff * a.vy;
    }
}
