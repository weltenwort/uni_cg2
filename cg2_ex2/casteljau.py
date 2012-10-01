from numpy import zeros, cross

class Casteljau(object):
    
    def __init__(self, matrix):
        self.matrix = matrix

    def evaluate_point(self, point):
        s, t = point
        matrix = self.matrix
        n = len(matrix)
        k = 1
        l = 1
        
        while k < (n - 1):
            temp_matrix = zeros((n, n - k))
            for j in range(n):
                for i in range(n - k):
                    temp_matrix[j, i] += (1 - s) * matrix[j, i] + s * matrix[j, i + 1]
            matrix = temp_matrix
            k += 1
            
        while l < (n - 1):
            temp_matrix = zeros((n - l, 2))
            for j in range(n- l):
                for i in range(2):
                    temp_matrix[j, i] += (1 - t) * matrix[j, i] + t * matrix[j + 1, i]
            matrix = temp_matrix
            l += 1
        
        temp_matrix = zeros((2, 1))
        i = 0
        for j in range(2):
            temp_matrix[j, i] += (1 - s) * matrix[j, i] + s * matrix[j, i + 1]
        s_vector = temp_matrix
        
        temp_matrix = zeros((1, 2))
        j = 0
        for i in range(2):
            temp_matrix[j, i] += (1 - t) * matrix[j, i] + t * matrix[j + 1, i]
        t_vector = temp_matrix
        
        tangent_s = [1, 0, n * (s_vector[1, 0] - s_vector[0, 0])]
        tangent_t = [0, 1, n * (t_vector[0, 1] - t_vector[0, 0])]
        normal = cross(tangent_s, tangent_t)
        
        result = (1 - t) * s_vector[0, 0] + t * s_vector[1, 0]
        
        return (result, normal)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            
        
