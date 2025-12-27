"""
Example SageMath code to test the language server.

This file demonstrates various SageMath features that the language
server should be able to handle.
"""

# Basic SageMath operations
x = var('x')
f(x) = x^2 + 2*x + 1

# Solve equations
solve(f(x) == 0, x)

# Calculus
derivative(f(x), x)
integral(f(x), x)

# Matrix operations
M = matrix([[1, 2], [3, 4]])
M.eigenvalues()

# Number theory
factor(2023)
is_prime(17)

# Symbolic computation
expand((x + 1)^3)
simplify(sin(x)^2 + cos(x)^2)

# Graphics
plot(f(x), (x, -5, 5))
