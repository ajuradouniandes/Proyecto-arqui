from django.db import models


class Product(models.Model):
    id_product = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

class Bodega(models.Model):
    id_bodega = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
class Shelve(models.Model):
    id_shelve= models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name='shelves')
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

class Inventory(models.Model):
    id_inventory = models.AutoField(primary_key=True)
    id_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    id_bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    id_shelve = models.ForeignKey(Shelve, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)