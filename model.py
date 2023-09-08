from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set, NewType

Quantity  = NewType("Quantity", int)
Sku       = NewType("Sku", str)
Reference = NewType("Reference", str)


""" record de uma ordem"""
@dataclass(frozen=True)
class Orderline:
    orderid: str
    sku    : Sku
    qty    : Quantity
    
""" Classe de estoque de um produto"""
class Batch:
    
    def __init__(self, ref: Reference, sku: Sku, qty: Quantity, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._avaible_quantity = qty
        self._allocations = set()  # type: Set[Orderline]
    
    def allocate(self, line: Orderline) -> bool:
        if self.can_allocate(line):
            self._avaible_quantity -= line.qty
            self._allocations.add(line) 

    # def __repr__(self) -> str:
    #     return f"ref: {self.reference}, sku: {self.sku}, ava_qty: {self._avaible_quantity}"
    
    def deallocate(self, line: Orderline):
        if line in self._allocations:
            self._allocations.remove(line)
            self._avaible_quantity += line.qty
        
    def can_allocate(self, line: Orderline) -> bool:
        if (line not in self._allocations):
            return self.sku == line.sku and self._avaible_quantity >= line.qty
    
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)
    
    def avaible_quantity(self) -> int:
        return self._avaible_quantity

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

class OutOfStock(Exception):
    pass