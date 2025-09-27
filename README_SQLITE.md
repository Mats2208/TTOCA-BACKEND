## 🗄️ Esquema de Base de Datos

### Tablas Principales
- **users** - Usuarios del sistema
- **empresas** - Empresas de cada usuario
- **cola_categorias** - Tipos de cola/categorías
- **turnos** - Turnos en las colas
- **turnos_actuales** - Control de turnos siendo atendidos

### Relaciones
- `empresas` ➜ `users` (un usuario puede tener varias empresas)
- `cola_categorias` ➜ `empresas` (una empresa puede tener varias categorías)
- `turnos` ➜ `cola_categorias` (una categoría puede tener varios turnos)

## 🛠️ Herramientas de Administración

### Script de Administración
```bash
python admin.py <comando>
```

**Comandos disponibles:**
- `stats` - Estadísticas generales del sistema
- `clean` - Limpiar turnos antiguos
- `activity` - Mostrar actividad por empresa
- `check` - Verificar integridad de la base de datos
- `repair` - Reparar posiciones de colas
- `backup` - Crear backup completo en JSON

### Ejemplos de uso:
```bash
# Ver estadísticas del sistema
python admin.py stats

# Limpiar turnos de más de 7 días
python admin.py clean 7

# Ver actividad por empresa
python admin.py activity

# Verificar integridad
python admin.py check

# Crear backup
python admin.py backup
```

## 🚀 Iniciando el Servidor

```bash
python app.py
```

El servidor automáticamente:
1. ✅ Inicializa la base de datos si no existe
2. ✅ Carga todos los datos persistentes
3. ✅ Configura la limpieza automática
4. ✅ Está listo para recibir peticiones

## 📊 Datos Migrados

### Estado de la Migración
- **👤 Usuarios:** 1 migrado exitosamente
- **🏢 Empresas:** 1 migrada exitosamente  
- **📋 Categorías:** 3 migradas exitosamente
- **🎫 Turnos:** 0 (no había turnos pendientes)

### Datos Preservados
- ✅ Credenciales de usuarios (hashes de contraseña)
- ✅ Información completa de empresas
- ✅ Configuraciones de categorías de cola
- ✅ Contadores de turnos
- ✅ Configuraciones personalizadas

## 🔧 Mantenimiento Automático

### Limpieza Automática
- Los turnos completados se eliminan automáticamente después de 24 horas
- Se ejecuta al cerrar la aplicación
- Mantiene la base de datos optimizada

### Backup Manual
```bash
python admin.py backup
```
Genera un archivo `backup_completo_YYYYMMDD_HHMMSS.json` con todos los datos.

## 🚨 Solución de Problemas

### Base de datos corrupta
```bash
# Eliminar y recrear
rm ttoca.db
python migrate.py
```

### Datos perdidos
```bash
# Restaurar desde backup JSON
# Los backups están en json_backup/
cp json_backup/*.backup ./
# Renombrar archivos
mv users.json.backup users.json
mv Queue.json.backup Queue.json
mv cola_config.json.backup cola_config.json
# Migrar nuevamente
python migrate.py
```

### Verificar integridad
```bash
python admin.py check
```

### Reparar posiciones de cola
```bash
python admin.py repair
```

## 📈 Ventajas de SQLite

1. **Sin instalación adicional** - Viene con Python
2. **Base de datos local** - Ideal para VPS
3. **ACID compliant** - Transacciones seguras
4. **Concurrencia** - Múltiples lecturas simultáneas
5. **Tamaño eficiente** - Solo ocupa el espacio necesario
6. **Respaldo fácil** - Un solo archivo `ttoca.db`

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Constraints de base de datos
- ✅ Transacciones atómicas
- ✅ Validación de integridad

## 📞 Compatibilidad de API

**¡IMPORTANTE!** Todas las APIs existentes siguen funcionando exactamente igual. No necesitas cambiar nada en tu frontend.

- ✅ Mismas rutas de API
- ✅ Misma estructura de respuestas
- ✅ Mismos códigos de estado
- ✅ Misma funcionalidad

## 🎯 Próximos Pasos Recomendados

1. **Probar completamente** - Verifica todas las funciones de tu app
2. **Monitorear rendimiento** - La app debería ser más rápida
3. **Configurar backups regulares** - Usar `admin.py backup`
4. **Eliminar archivos JSON** - Una vez que confirmes que todo funciona
5. **Documentar para tu equipo** - Comparte este README

## 🏆 ¡Felicidades!

Tu backend TTOCA ahora es **más robusto, confiable y escalable**. Los datos están seguros y el sistema está preparado para crecer.

---

**¿Preguntas o problemas?** 
- Revisa los logs con `python admin.py check`
- Crea un backup con `python admin.py backup`
- Consulta las estadísticas con `python admin.py stats`