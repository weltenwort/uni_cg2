import logging
from numpy import array, zeros, power, vdot, cross
from numpy.linalg import norm
from scipy.spatial import KDTree
from scipy.linalg import solve

class MinSquares(object):
    
    def __init__(self, surface):
        self._log = logging.getLogger('MinSquares')
        self.tree = surface.tree
        self.vertex_dict = surface.mapping
        self.pointlist = surface.points
        
    def wendland(self, distance, radius):
        return power(1-(distance/(radius + 0.1)), 4) * (4*(distance/(radius + 0.1)) + 1)
        
    def selectPoints(self, point, k):
        return self.tree.query(point, k)
        
    def solveEquations(self, point):
        matrix = zeros((6, 6))
        vector = zeros(6)
        distances, indices = self.selectPoints(point, 6)
        max_radius = distances[-1]
        selected_points = [self.pointlist[i] for i in indices]
        
        for selected_point in selected_points:
            u, v = selected_point
            f = self.vertex_dict[selected_point]
            distance = norm(array(selected_point) - array(point), 2)
            theta = self.wendland(distance, max_radius)
            
            matrix[0,0] += theta
            matrix[0,1] += theta * u
            matrix[0,2] += theta * v
            matrix[0,3] += theta * power(u, 2)
            matrix[0,4] += theta * u * v
            matrix[0,5] += theta * power(v, 2)
            
            matrix[1,0] += theta * u
            matrix[1,1] += theta * power(u, 2)
            matrix[1,2] += theta * u * v
            matrix[1,3] += theta * power(u, 3)
            matrix[1,4] += theta * power(u, 2) * v
            matrix[1,5] += theta * u * power(v, 2)
            
            matrix[2,0] += theta * v
            matrix[2,1] += theta * u * v
            matrix[2,2] += theta * power(v, 2)
            matrix[2,3] += theta * power(u, 2) * v
            matrix[2,4] += theta * u * power(v, 2)
            matrix[2,5] += theta * power(v, 3)
            
            matrix[3,0] += theta * power(u, 2)
            matrix[3,1] += theta * power(u, 3)
            matrix[3,2] += theta * power(u, 2) * v
            matrix[3,3] += theta * power(u, 4)
            matrix[3,4] += theta * power(u, 3) * v
            matrix[3,5] += theta * power(u, 2) * power(v, 2)
            
            matrix[4,0] += theta * u * v
            matrix[4,1] += theta * power(u, 2) * v
            matrix[4,2] += theta * u * power(v, 2)
            matrix[4,3] += theta * power(u, 3) * v
            matrix[4,4] += theta * power(u, 2)  * power(v, 2)
            matrix[4,5] += theta * u * power(v, 3)
            
            matrix[5,0] += theta * power(v, 2)
            matrix[5,1] += theta * u * power(v, 2)
            matrix[5,2] += theta * power(v, 3)
            matrix[5,3] += theta * power(u, 2) * power(v, 2)
            matrix[5,4] += theta * u * power(v, 3)
            matrix[5,5] += theta * power(v, 4)
            
            vector[0] += theta * f
            vector[1] += theta * f * u
            vector[2] += theta * f * v
            vector[3] += theta * f * power(u, 2)
            vector[4] += theta * f * u * v
            vector[5] += theta * f * power(v, 2)
            
        x, y = point
        coefficients = solve(matrix, vector)
        variables = array([1, x, y, power(x, 2), x * y, power(y, 2)])
        z = vdot(coefficients, variables)
        zdx = coefficients[1] + 2 * coefficients[3] * x + coefficients[4] * y
        zdy = coefficients[2] + 2 * coefficients[5] * y + coefficients[4] * x
        normal = cross([1, 0, zdx], [0, 1, zdy])
        return (z, normal)
            

    
    
    
    
    
    
    
    
    
    
    
    
