# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 17:47:04 2024

@author: jocgo
"""
import pandas as pd
import matplotlib.pyplot as plt

#parametros

# Agrupar por periodo
periodo = 15  # Puedes cambiar este valor a 7 (semana), 0.5 (medio día), 15 (dos semanas) o 30 (mes) según sea necesario


#data

df=pd.read_csv("inventario.csv", parse_dates=['fecha y hora'])

#agrupar data según periodo


# Función para agrupar el DataFrame según el parámetro periodo
def agrupar_por_periodo(df, periodo):
    if periodo == 1:
        # Agrupar por tienda, por día, por item
        df['fecha'] = df['fecha y hora'].dt.date
        df_grouped = df.groupby(['tienda', 'fecha', 'item'])['cantidad'].sum().reset_index()
    
    elif periodo == 7:
        # Agrupar por semana
        df['semana'] = df['fecha y hora'].dt.to_period('W').apply(lambda r: r.start_time)
        df_grouped = df.groupby(['tienda', 'semana', 'item'])['cantidad'].sum().reset_index()
    
    elif periodo == 0.5:
        # Agrupar por las primeras doce horas y las segundas doce horas del día
        df['hora'] = df['fecha y hora'].dt.hour
        df['periodo_dia'] = df['hora'].apply(lambda x: 'primeras 12 horas' if x < 12 else 'segundas 12 horas')
        df_grouped = df.groupby(['tienda', 'fecha y hora', 'periodo_dia', 'item'])['cantidad'].sum().reset_index()

    elif periodo == 15: 
        # Agrupar cada dos semanas (1-15 y 16-fin de mes) 
        df['quincena'] = df['fecha y hora'].apply(lambda x: f"{x.year}-{x.month:02d}-{'1-15' if x.day <= 15 else '16-fin'}") 
        df_grouped = df.groupby(['tienda', 'quincena', 'item'])['cantidad'].sum().reset_index() 
        # Convertir las quincenas en fechas para el gráfico 
        df_grouped['quincena'] = pd.to_datetime(df_grouped['quincena'].str.replace('fin', '15') + ' 00:00:00')
    elif periodo == 30:
        # Agrupar por mes
        df['mes'] = df['fecha y hora'].dt.to_period('M').apply(lambda r: r.start_time)
        df_grouped = df.groupby(['tienda', 'mes', 'item'])['cantidad'].sum().reset_index()
    
    return df_grouped

# Ejemplo de uso
# Supongamos que ya tienes el DataFrame df
# df = pd.read_csv('ruta_al_archivo.csv', parse_dates=['fecha y hora'])


df_agrupado = agrupar_por_periodo(df, periodo)

# Mostrar el DataFrame agrupado
print(df_agrupado)

# Función para graficar los datos agrupados por tienda y fruta
def graficar_agrupado(df, periodo, tienda, fruta):
    df_agrupado = agrupar_por_periodo(df, periodo)
    df_filtro = df_agrupado[(df_agrupado['tienda'] == tienda) & (df_agrupado['item'] == fruta)]
    
    plt.figure(figsize=(14, 7), dpi=150) # Tamaño y resolución más alta para el gráfico
    if periodo == 1:
        df_filtro.plot(x='fecha', y='cantidad', kind='line', title=f'Demanda de {fruta} en {tienda} por día')
    elif periodo == 7:
        df_filtro.plot(x='semana', y='cantidad', kind='line', title=f'Demanda de {fruta} en {tienda} por semana')
    elif periodo == 0.5:
        df_filtro.plot(x='fecha y hora', y='cantidad', kind='line', title=f'Demanda de {fruta} en {tienda} por período de 12 horas')
    elif periodo == 15:
        df_filtro.plot(x='quincena', y='cantidad', kind='line', title=f'Demanda de {fruta} en {tienda} cada dos semanas')
    elif periodo == 30:
        df_filtro.plot(x='mes', y='cantidad', kind='line', title=f'Demanda de {fruta} en {tienda} por mes')
    
    plt.xlabel('Periodo')
    plt.ylabel('Cantidad vendida')
    plt.show()

# Ejemplo de uso
# Supongamos que ya tienes el DataFrame df
# df = pd.read_csv('ruta_al_archivo.csv', parse_dates=['fecha y hora'])

# Parámetros de ejemplo
tienda = "Supermercado A"  # Elige una tienda específica
fruta = "Manzanas"  # Elige una fruta específica

# Graficar los datos agrupados
graficar_agrupado(df, periodo, tienda, fruta)

