def allocate(order, warehouse, shipments):
    allocation = {}
    for source in shipments + [warehouse]:
        allocation.update(allocation_from(order, source))
    return allocation

def allocation_from(order, source):
    return {
        sku: source
        for sku, quantity in order.items()
        if sku in source
        and source[sku] > quantity
    }
