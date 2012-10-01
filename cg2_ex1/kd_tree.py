from math import abs

from cg2kit import BoundingBox
from numpy import *

class Node(object):
    def __init__(self, location, splitaxis, left_child, right_child):
        self.location    = location
        self.splitaxis   = splitaxis
        self.left_child  = left_child
        self.right_child = right_child
    
    def is_leaf(self):
        return (not self.right_child) and (not self.left_child)

    def get_bbox(self):
        bbox = BoundingBox()
        bbox.addPoint(self.location)
        if self.left_child:
            bbox.addBoundingBox(self.left_child.get_bbox())
        if self.right_child:
            bbox.addBoundingBox(self.right_child.get_bbox())
        return bbox

    def approx_distance(self, point):
        bbox = self.get_bbox()
        center = bbox.center()
        dir = array(center) - point
        bounds = bbox.getBounds(dir)
        max_distance = 0
        for axis in range(len(self.location)):
            t = self.location[axis] - bounds[1][axis]
            if t > max_distance:
                max_distance = t
            t = bounds[1][axis] - self.location[axis]
            if t > max_distance:
                max_distance = t
        return max_distance

    def exact_sq_distance(self, point):
        return sum((self.location - point)**2)

    def iter_vertices(self):
        stack = [self, ]
        while stack:
            node = stack.pop()
            yield node.location
            if node.left_child:
                stack.append(node.left_child)
            if node.right_child:
                stack.append(node.right_child)

class KdTree(object):
            
    def __init__(self, point_list):
        self.root = self.buildTree(point_list)
        self.nodecount = 0
        self._count_nodes(self.root)
        #self.knearest = () saving the results within the tree makes no sense since they depend on various parameters
        #self.inradius = ()
        
    def buildTree(self, point_list, depth = 0):
        if not point_list:
            return None
        else:
            # Select axis based on depth so that axis cycles through all valid values
            point_dimension = len(point_list[0]) # assumes all points have the same dimension
            axis = depth % point_dimension
         
            # Sort point list and choose median as pivot element
            point_list.sort(key=lambda point: point[axis])
            median = len(point_list)/2 # choose median
         
            # Create node and construct subtrees
            return Node(
                location    = point_list[median],
                splitaxis   = axis,
                left_child  = self.buildTree(point_list[0:median], depth+1),
                right_child = self.buildTree(point_list[median+1:], depth+1))
    
    def _count_nodes(self, rootnode):
        self.nodecount += 1
        if rootnode.left_child:
            self._count_nodes(rootnode.left_child)
        if rootnode.right_child:
            self._count_nodes(rootnode.right_child)

    def iter_vertices(self):
        stack = [self.root, ]
        while stack:
            node = stack.pop()
            yield node.location
            if node.left_child:
                stack.append(node.left_child)
            if node.right_child:
                stack.append(node.right_child)
    
    def collectKNearest(self, k, point):
        knearest = []
        self._collectKNearest_recursive(k, self.root, point, knearest)
        return knearest
        
    #TODO: fix type errors, test functionality
    def _collectKNearest_recursive(self, k, rootnode, point, knearest):
        point_dimension = len(point)
        axis = rootnode.splitaxis
        walked_right = False
        walked_left = False
        
        if (point[axis] >= rootnode.location[axis]) and (not rootnode.is_leaf()) and rootnode.right_child:
            self._collectKNearest_recursive(k, rootnode.right_child, point, knearest)
            walked_right = True
        elif (point[axis] < rootnode.location[axis]) and (not rootnode.is_leaf()) and rootnode.left_child:
            self._collectKNearest_recursive(k, rootnode.left_child, point, knearest)
            walked_left = True
        
        distance = sum(square(rootnode.location - array(point)))
        if len(knearest) < k: 
            knearest.append([rootnode,distance])
        else: 
            max_distance = max(point[1] for point in knearest)
            if distance < max_distance:
                for index,point in enumerate(knearest):
                    if point[1] == max_distance:
                        elementindex = index
                del knearest[elementindex]
                knearest.append([rootnode,distance])
            
        max_distance = max(point[1] for point in knearest)
        if square(float(rootnode.location[axis]) - float(point[axis])) < max_distance:
            if walked_right and not walked_left and rootnode.left_child:
                self._collectKNearest_recursive(k, rootnode.left_child, point, knearest)
            elif walked_left and not walked_right and rootnode.right_child:
                self._collectKNearest_recursive(k, rootnode.right_child, point, knearest)
                                   
    
    def collectInRadius(self, point, radius):
        inradius = []
        self._collectInRadius_recursive(r, self.root, point, inradius)
        return inradius
        
    def _collectInRadius_recursive(self, point, radius, node, inradius):
        sq_radius = radius**2
        if node.left_child or node.right_child:
            if node.left_child:
                if node.left_child.approx_distance(point)**2 <= sq_radius:
                    self._collectInRadius_recursive(point, radius, node.left_child, inradius)
                elif node.left_child
                    inradius.extend(node.left_child.iter_vertices())
        else:
            if node.exact_sq_distance(point) <= sq_radius:
                inradius.append(node)

        #if rootnode is a leaf: report it if it lies in r
        #elif region(left_child) is fully contained in r: report left subtree
        #elif region(left_child) intersects r: collectInRadius(r, left_child, point, depth+1)
        
        #if region(right_child) is fully contained in r: report right subtree
        #elif region(right_child) intersects r: collectInRadius(r, right_child, point, depth+1)
        pass
