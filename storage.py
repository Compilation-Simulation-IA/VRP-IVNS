from typing import List
from math import sqrt, pi, e
from typing import List, Tuple, Optional, Union, Dict
import numpy as np
import networkx as nx
import random

""" Map Structures """

class Stop:
    """Representa las paradas donde se encuentran los clientes"""
    def __init__(self, ID: int, total_client: int, location: Tuple[float, float], time_waiting: int):
        self.ID = ID
        self.total_client = total_client
        self.time_waiting = time_waiting #time_waiting es en minutos
        self.location = location

    def __repr__(self) -> str:
        return f"<Stop({self.id})>"
    
    def __str__(self) -> str:
        return f"<Stop: ID: {self.id}, Location: {self.location}>"

    def __gt__(self, other_stop):
        return self.index > other_stop.index

    def increase_wait(self, minutes):
        self.time_waiting += minutes

    def decrease_wait(self, minutes):
        self.time_waiting = max(self.time_waiting - minutes, 0)

    def add_client(self, client: Optional[int] = None):
        if client is None:
            self.total_client += 1
        else:
            self.total_client += client
    
    def remove_client(self, client: Optional[int] = None):
        if client is None:
            self.total_client -= 1
        else:
            self.total_client = min(0, self.total_client - client)


class Warehouse:
    """Representa un almacén o depósito central."""
    def __init__(self, ID: int, location: Tuple[float, float] ):
        self.ID = ID
        self.location = location
    
    def __repr__(self) -> str:
        return f"<Warehouse({self.ID})>"

    def __str__(self) -> str:
        return f"<Warehouse: ID: {self.ID}, Location: {self.location}>"
        
#class Node:
#    """Nodos del grafo. La variable value puede ser un Stop, Warehouse o 
#    simplemente una parada vacia(no tiene que recoger a nadie)"""
#
#    def __init__(self, value: Union[None, Stop, Warehouse]):
#        self.ID = value.ID  # Identificador único del nodo
#        self.location = value.location  # Tupla con las coordenadas (latitud, longitud) de la ubicación del nodo
#        self.value = value
#
#    def __repr__(self) -> str:
#        return f"<Node({self.value})>"
#    
#    def __str__(self) -> str:
#        return f"<Node: Value: {self.value}>"
#
#class Edge:
#    def __init__(self, start: Node, end: Node, cost: float):
#        self.start = start  # Nodo de inicio de la arista
#        self.end = end  # Nodo de fin de la arista
#        self.cost = cost  # Costo de recorrer la arista
#        # Puede estar vacio.
#    
#    def __repr__(self) -> str:
#        return f"<Edge: Start {self.start}, End: {self.end}>"
#    
#    def __str__(self) -> str:
#        return f"<Edge: Start {self.start}, End: {self.end}, Cost: {self.cost}>"
#
#
#class Graph:
#    def __init__(self):
#        self.graph = nx.Graph()  # Crear un grafo vacío 
#
#    def __repr__(self) -> str:
#        return f"<Graph: Nodes Number: {len(self.graph.nodes)}, Edges Number: {len(self.graph.edges)}>"
#    
#    def __str__(self) -> str:
#        return f"<Graph: Nodes Number: {len(self.nodes)}, Edges Number: {len(self.edges)}>"
#    
#    def get_edge(self, start: Dict, end: Dict) -> Edge:
#        for edge in self.graph.edges: #self.graph.edges VER SI QUITO LA LISTA DE NODES Y EDGES
#            if edge.start == start.ID and edge.end == end.ID:
#                return edge
#        return None  # Si no se encuentra la arista, devolver None
#    
#    def get_neighbors(self, node: Dict) -> List[Dict]:
#        neighbors = []
#        for neighbor in self.graph.neighbors(node.ID):  # Obtener vecinos del nodo a través del grafo
#            neighbors.append(self.get_node_by_ID(neighbor))
#        return neighbors
#    
#    def get_node_by_ID(self, ID: int) -> Dict:
#        for node in self.nodes:
#            if node.ID == ID:
#                return node
#        return None  # Si no se encuentra el nodo, devolver None

class Distribution_Type: 
    """ Clase para guardar todas las distribuciones que siguen las variables del problema"""
    def __init__(self):
        pass

    def generateExponential(self, lambda_value):
        return -(lambda_value * math.log(random.random()))
    
    def generateUniform(self, a, b):
        if a <= b :
            return random.uniform(a,b)
        raise Exception("Invalid argument.")

class Route:
    """Representa la ruta que sigue el vehiculo para recoger a los clientes y 
    llegar a su destino"""
    def __init__(self, ID: int, stops: List[Dict]):
        self.ID = ID
        self.actual_stop_index = 0
        self.stops = stops
        self.cost = 0 # Representa el costo de realizar la ruta

    def __repr__(self) -> str:
        """Representacion de la clase Route"""
        return f"<Route({self.ID})>"

    def __str__(self) -> str:
        """Representacion de la clase Route"""
        return f"<Route: ID {self.ID}, Stops Total Count: {len(self.stops)}>"

    def next_stop(self, actual_stop: Dict) -> Union[Dict,None]:
        index = self.stops.index(actual_stop)
        if index == len(self.stops) - 1:
            return None
        return self.stops[index + 1]

    def add_stop(self, stop: Dict, position: Optional[int] = None):
        """Añade una parada a la ruta en la posición indicada. Si no se especifica 
        la posición, se añade al final de la ruta."""
        if position is None:
            self.stops.append(stop)
        else:
            self.stops.insert(position, stop)

    def remove_stop(self, stop: Stop):
        """Elimina una parada de la ruta."""
        self.stops.remove(stop)

    def swap_stops(self, stop1: Stop, stop2: Stop):
        """Intercambia dos paradas de la ruta."""
        index1 = self.stops.index(stop1)
        index2 = self.stops.index(stop2)
        self.stops[index1], self.stops[index2] = self.stops[index2], self.stops[index1]
    
    def get_cost(self) -> float:
        """Calcula el costo total de la ruta."""
        self.cost = 0
        for stop in self.stops:
            self.cost += stop.value.cost
        return self.cost


