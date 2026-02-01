from django.urls import path
from . import views

urlpatterns = [
    # Views de Interface Web
    path("", views.home, name="home"),
    path("testar/", views.testar_estrategias, name="testar_estrategias"),
    path("criar/", views.criar_pedido_form, name="criar_pedido_form"),
    path("pedidos/", views.listar_pedidos, name="listar_pedidos"),
    path("pedidos/<int:pedido_id>/", views.detalhes_pedido, name="detalhes_pedido"),
    
    # APIs
    path("api/calcular/", views.calcular_estrategias_api, name="calcular_api"),
    path("criar-pedido/", views.criar_pedido, name="criar_pedido"),
    path(
        "pedido/<int:pedido_id>/",
        views.calcular_pedido_dinamico,
        name="calcular_pedido",
    ),
]
