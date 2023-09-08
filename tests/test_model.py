from datetime import date, timedelta
import pytest
from model import Batch, Orderline, Quantity, Sku, OutOfStock
from typing import List

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)
    

""" Testing Allocate"""
def make_batch_and_line(sku: Sku, batch_qty: Quantity, line_qty: Quantity):
    return (
        Batch("batch-123", sku, batch_qty, eta=today),
        Orderline("order-123", sku, line_qty)
    )
    
def test_allocating_to_a_batch_reduces_the_available_quantity():
    Batch, line = make_batch_and_line("RED-CHAIR", 200, 3)
    
    Batch.allocate(line)
    print(f"A quantidade no deposito e de: {Batch.avaible_quantity}")
    assert Batch.avaible_quantity() == 197

def test_can_allocate_if_available_greater_than_required():
    Batch, line = make_batch_and_line("RED-CHAIR", 200, 3)
    assert Batch.can_allocate(line)

def test_cannot_allocate_if_available_smaller_than_required():
    Batch, line = make_batch_and_line("RED-CHAIR", 10, 20)
    assert Batch.can_allocate(line) is False

def test_can_allocate_if_available_equal_to_required():
    Batch, line = make_batch_and_line("RED-CHAIR", 20, 20)
    assert Batch.can_allocate(line)

def test_dealocate():
    Batch, line = make_batch_and_line("RED-CHAIR", 20, 5)
    line2 = Orderline('order2', "RED-CHAIR", 3)
    Batch.allocate(line)
    Batch.allocate(line2)
    Batch.deallocate(line2)
    assert Batch.avaible_quantity() == 15

def test_can_only_deallocate_allocated_line():
    Batch, line = make_batch_and_line("RED-CHAIR", 20, 5)
    Batch.deallocate(line)
    
    assert Batch.avaible_quantity() == 20
    
# def test_prefers_warehouse_batches_to_shipments():
#     pytest.fail("todo")

def test_allocate_same_line():
    Batch, line = make_batch_and_line("RED-CHAIR", 20, 5)
    Batch.allocate(line)
    Batch.allocate(line)
    
    assert Batch.avaible_quantity() == 15

def test_can_not_allocate_if_different_skus():
    batch = Batch("rapido-ref", "HIGHBROW-POSTER", 100, eta=today)
    line  = Orderline("RED-CHAIR")


""" Testing Batches"""
def test_prefers_earlier_batches():
    earlier_batch = Batch("rapido-ref", "HIGHBROW-POSTER", 100, eta=today)
    medim_batch   = Batch("normal-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    late_batch    = Batch("demorado-ref", "HIGHBROW-POSTER", 100, eta=later)
    
    line = Orderline("Order-id", "HIGHBROW-POSTER", 10)
    allocate(line, [earlier_batch, medim_batch, late_batch])
    
    assert earlier_batch.avaible_quantity() == 90
    assert medim_batch.avaible_quantity() == 100
    assert late_batch.avaible_quantity() == 100
    
def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = Orderline("oref", "HIGHBROW-POSTER", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
   
    assert allocation == in_stock_batch.reference
    assert allocation != shipment_batch.reference
 
 
def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch('batch1', 'SMALL-FORK', 10, eta=today)
    allocate(Orderline('order1', 'SMALL-FORK', 10), [batch])
    
    with pytest.raises(OutOfStock, match='SMALL-FORK'):
        allocate(Orderline('order2', 'SMALL-FORK', 1), [batch])
 
 
def allocate(line: Orderline, batches: List[Batch]) -> str:
    try:
        batch = next(
            b for b in sorted(batches) if b.can_allocate(line)
        )
    except StopIteration:
        raise OutOfStock(f"Sem estoque para sku {line.sku}")
    
    batch.allocate(line)
    return batch.reference
