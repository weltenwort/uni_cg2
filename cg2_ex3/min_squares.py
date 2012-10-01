import logging
from numpy import array, zeros, power, vdot, cross, outer
from numpy.linalg import norm
from scipy.spatial import KDTree
from scipy.linalg import solve

#try:
#    import psyco
#    psyco.log()
#    psyco.full()
#    psyco.bind(MinSquares.evaluatePoint)
#except ImportError:
#    pass

class MinSquares(object):
    
    def __init__(self, surface):
        self._log = logging.getLogger('MinSquares')
        self.needed_points = 7
        self.tree = surface.tree
        self.pointlist = surface.points
        self.normallist = surface.normals
        self.distance_threshold = surface.distance_threshold
        #self.distance_threshold = 50
        self.eps = surface.eps
        self.setEps()
        
    def setEps(self):
        for index, point in enumerate(self.pointlist):
            while self.tree.query(array(point) + (self.eps * array(self.normallist[index])), 1)[1] != index:
                self.eps = self.eps / 2
            while self.tree.query(array(point) - (self.eps * array(self.normallist[index])), 1)[1] != index:
                self.eps = self.eps / 2
        
    def wendland(self, distance, radius):
        return power(1-(distance/(radius + 0.1)), 4) * (4*(distance/(radius + 0.1)) + 1)
        
    def selectPoints(self, point, k):
        return self.tree.query(point, k)
        
    def solveEquations(self, point, degree):
        point = array(point)
        distances, indices = self.selectPoints(point, self.needed_points)
        if distances[-1] > self.distance_threshold:
            nearest_distance = distances[0]
            nearest_index = indices[0]
            nearest_point = array(self.pointlist[nearest_index])
            nearest_point_normal = array(self.normallist[nearest_index])
            if vdot(point - nearest_point, nearest_point_normal) >= 0:
               direction = 1
            else:
                direction = -1
            value = direction * nearest_distance
            normal = nearest_point_normal
        else:
            delta = power(10.0, -5)
            dx = point + delta * array([1, 0, 0])
            dy = point + delta * array([0, 1, 0])
            dz = point + delta * array([0, 0, 1])
            
            value = self.evaluatePoint(point, distances, indices, degree)
            
            gradient = array([(self.evaluatePoint(dx, distances, indices, degree) - value) / delta,
                              (self.evaluatePoint(dy, distances, indices, degree) - value) / delta,
                              (self.evaluatePoint(dz, distances, indices, degree) - value) / delta
                              ])
            if norm(gradient, 2) != 0:
                normal = gradient / norm(gradient, 2)
            else:
                normal = gradient
        
        return (value, normal)
        
    def evaluatePoint(self, point, distances, indices, degree=1):
        x, y, z = point
        if degree == 1:
            dim = 1
            variables = array([1])
        elif degree == 2:
            dim = 4
            variables = array([1, x, y, z])
        else:
            dim = 10
            variables = array([1, x, y, z, x*y, y*z, x*z, power(x, 2), power(y, 2), power(z, 2)])
        matrix = zeros((dim, dim))
        vector = zeros(dim)
        max_radius = distances[-1]
        
        for index in indices:
            selected_point = array(self.pointlist[index])
            selected_normal = array(self.normallist[index])
            
            x1, y1, z1 = selected_point
            x2, y2, z2 = selected_point + (self.eps * selected_normal)
            x3, y3, z3 = selected_point - (self.eps * selected_normal)
            
            if degree == 1:
                b1 = array([1])
                b2 = array([1])
                b3 = array([1])
            elif degree == 2:
                b1 = array([1, x1, y1, z1])
                b2 = array([1, x2, y2, z2])
                b3 = array([1, x3, y3, z3])
            else:
                b1 = array([1, x1, y1, z1, x1*y1, y1*z1, x1*z1, power(x1, 2), power(y1, 2), power(z1, 2)])
                b2 = array([1, x2, y2, z2, x2*y2, y2*z2, x2*z2, power(x2, 2), power(y2, 2), power(z2, 2)])
                b3 = array([1, x3, y3, z3, x3*y3, y3*z3, x3*z3, power(x3, 2), power(y3, 2), power(z3, 2)])
                
            distance1 = norm(selected_point - point, 2)
            distance2 = norm(selected_point + (self.eps * selected_normal) - point, 2)
            distance3 = norm(selected_point - (self.eps * selected_normal) - point, 2)
            
            theta1 = self.wendland(distance1, max_radius)
            theta2 = self.wendland(distance2, max_radius)
            theta3 = self.wendland(distance3, max_radius)
            
            matrix1 = theta1 * outer(b1, b1)
            matrix2 = theta2 * outer(b2, b2)
            matrix3 = theta3 * outer(b3, b3)
            
            vector1 = 0 * b1
            vector2 = self.eps * theta2 * b2
            vector3 = self.eps * theta3 * b3
            
            matrix += matrix1 + matrix2 + matrix3
            vector += vector1 + vector2 - vector3
        
        coefficients = solve(matrix, vector)
        value = vdot(coefficients, variables)

        return value
            
