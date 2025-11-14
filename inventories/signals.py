from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import OrderCreation, AuditLog

@receiver(pre_save, sender=OrderCreation)
def log_critical_changes(sender, instance, **kwargs):
    if not instance.pk:
        return  # si es un pedido nuevo, no se audita

    previous = OrderCreation.objects.get(pk=instance.pk)
    changes = []

    # Detectar cambios críticos
    if previous.status != instance.status:
        changes.append(f"Estado: {previous.status} → {instance.status}")

    if previous.quantity != instance.quantity:
        changes.append(f"Cantidad: {previous.quantity} → {instance.quantity}")

    if changes:
        AuditLog.objects.create(
            user=getattr(instance, "_modified_by", None),
            order=instance,
            action_type="cambio_estado",
            detail=", ".join(changes)
        )
