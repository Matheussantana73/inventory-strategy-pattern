FROM nginx:alpine

# Remover configuração padrão
RUN rm /etc/nginx/conf.d/default.conf

# Copiar nossa configuração
COPY nginx.conf /etc/nginx/conf.d/

# Expor porta
EXPOSE 80

# Comando de execução
CMD ["nginx", "-g", "daemon off;"]
