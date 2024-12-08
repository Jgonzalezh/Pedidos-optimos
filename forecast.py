# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 17:47:04 2024

@author: jocgo
"""
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from datetime import timedelta

#parametros

# Agrupar por periodo
periodo = 1  # Puedes cambiar este valor a 7 (semana), 0.5 (medio día), 15 (dos semanas) o 30 (mes) según sea necesario
forecast_days=60

#data
fecha_y_hora='fecha y hora'
item='item'
Q='cantidad'
df=pd.read_csv("inventario.csv", parse_dates=[fecha_y_hora])
import pandas as pd

# Función para crear un rango de fechas completo
def crear_rango_fechas(df, periodo):
    fecha_inicial = df['fecha y hora'].min().floor('D')
    fecha_final = df['fecha y hora'].max().ceil('D')
    if periodo == 1:
        fechas = pd.date_range(fecha_inicial, fecha_final, freq='D')
    elif periodo == 7:
        fechas = pd.date_range(fecha_inicial, fecha_final, freq='W')
    elif periodo == 0.5:
        fechas = pd.date_range(fecha_inicial, fecha_final, freq='12H')
    elif periodo == 15:
        fechas = pd.date_range(fecha_inicial, fecha_final, freq='15D')
    elif periodo == 30:
        fechas = pd.date_range(fecha_inicial, fecha_final, freq='M')
    return fechas

# Función para agrupar el DataFrame según el parámetro periodo
def agrupar_por_periodo(df, periodo):
    fechas_completas = crear_rango_fechas(df, periodo)
    tiendas = df['tienda'].unique()
    items = df['item'].unique()
    
    if periodo == 1:
        # Agrupar por tienda, por día, por item
        df['fecha'] = df['fecha y hora'].dt.date
        df_grouped = df.groupby(['tienda', 'fecha', 'item'])[['cantidad', 'precio']].sum().reset_index()
    
    elif periodo == 7:
        # Agrupar por semana
        df['semana'] = df['fecha y hora'].dt.to_period('W').apply(lambda r: r.start_time)
        df_grouped = df.groupby(['tienda', 'semana', 'item'])[['cantidad', 'precio']].sum().reset_index()
        df_grouped.rename(columns={'semana': 'fecha'}, inplace=True)
    
    elif periodo == 0.5:
        # Agrupar por las primeras doce horas y las segundas doce horas del día
        df['hora'] = df['fecha y hora'].dt.hour
        df['periodo_dia'] = df['hora'].apply(lambda x: 'primeras 12 horas' if x < 12 else 'segundas 12 horas')
        df_grouped = df.groupby(['tienda', 'fecha y hora', 'periodo_dia', 'item'])[['cantidad', 'precio']].sum().reset_index()
        df_grouped.rename(columns={'fecha y hora': 'fecha'}, inplace=True)

    elif periodo == 15:
        # Agrupar cada dos semanas (1-15 y 16-fin de mes)
        df['quincena'] = df['fecha y hora'].apply(lambda x: f"{x.year}-{x.month:02d}-{'01-15' if x.day <= 15 else '16-31'}")
        df_grouped = df.groupby(['tienda', 'quincena', 'item'])[['cantidad', 'precio']].sum().reset_index()
        # Convertir las quincenas en fechas para el gráfico
        df_grouped['quincena'] = pd.to_datetime(df_grouped['quincena'])
        df_grouped.rename(columns={'quincena': 'fecha'}, inplace=True)

    elif periodo == 30:
        # Agrupar por mes
        df['mes'] = df['fecha y hora'].dt.to_period('M').apply(lambda r: r.start_time)
        df_grouped = df.groupby(['tienda', 'mes', 'item'])[['cantidad', 'precio']].sum().reset_index()
        df_grouped.rename(columns={'mes': 'fecha'}, inplace=True)
    
    # Crear DataFrame con todas las combinaciones de fechas, tiendas y items
    todas_comb = pd.MultiIndex.from_product([tiendas, fechas_completas, items], names=['tienda', 'fecha', 'item']).to_frame(index=False)
    
    # Convertir las fechas de todas_comb al mismo tipo de dato
    todas_comb['fecha'] = pd.to_datetime(todas_comb['fecha'])
    df_grouped['fecha'] = pd.to_datetime(df_grouped['fecha'])
    
    # Unir con el DataFrame agrupado para asegurar que no haya periodos faltantes
    df_grouped_completo = todas_comb.merge(df_grouped, on=['tienda', 'fecha', 'item'], how='left').fillna(0)
    
    return df_grouped_completo

# Ejemplo de uso
# Supongamos que ya tienes el DataFrame df
# df = pd.read_csv('ruta_al_archivo.csv', parse_dates=['fecha y hora'])

# Agrupar por periodo
periodo = 1  # Puedes cambiar este valor a 7, 0.5, 15 o 30 según sea necesario
df_agrupado = agrupar_por_periodo(df, periodo)

# Mostrar el DataFrame agrupado
print(df_agrupado)


# Función para agrupar el DataFrame según el parámetro periodo
def agrupar_por_periodo2(df, periodo):
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
tienda = "Supermercado B"  # Elige una tienda específica
fruta = "Uvas"  # Elige una fruta específica

# Graficar los datos agrupados
graficar_agrupado(df, periodo, tienda, fruta)

class Time_Series:
    def __init__(self, data_csv,periodo,forecast_days):
        self.data= data_csv
        self.df=df=pd.read_csv(data_csv, parse_dates=[fecha_y_hora])
        self.periodo=periodo
        self.agrupado=agrupar_por_periodo(self.df, self.periodo)
        #definir test
        # Encontrar la fecha más antigua y la fecha más reciente 
        self.fecha_menor = df['fecha y hora'].min() 
        self.fecha_mayor = df['fecha y hora'].max()
        self.diferencia_dias = (self.fecha_mayor - self.fecha_menor).days
        self.forecast_days=forecast_days
        if self.diferencia_dias > 3*forecast_days:
            #print(True)
            x = self.diferencia_dias/3*2 # Puedes cambiar este valor al número de días que desees 
            # Calcular la nueva fecha 
            self.fecha_end_training = self.fecha_menor + timedelta(days=x)
        
        
        ####Tiene que crear diferentes nombres de fecha para los diferentes periodos que diste
        if self.periodo==1:
            self.fecha='fecha'
            
        # Crear el DataFrame df_train con las filas entre fecha_A y fecha_B 
        self.df_train = df_agrupado[(df_agrupado[self.fecha] >= self.fecha_menor) & (df_agrupado[self.fecha] <= self.fecha_end_training)]
        # Crear el DataFrame df_test con las filas desde fecha_B+1 día hasta fecha_C 
        self.df_test = df_agrupado[(df_agrupado[self.fecha] > self.fecha_end_training) & (df_agrupado[self.fecha] <= self.fecha_mayor)]
        print("DataFrame de entrenamiento (self.df_train):") 
        print(self.df_train) 
        print("\nDataFrame de prueba (self.df_test):") 
        print(self.df_test)
    def prophet (self):
        model=Prophet()
        df_prophet=self.df_train
        
        df_prophet.rename(columns={self.fecha:'ds', Q: 'y'}, inplace=True)
        
        print(df_prophet.columns,df_prophet.dtypes)
        model.fit(df_prophet)
        future = model.make_future_dataframe(self.forecast_days)
        forecast = model.predict(future)
        print(future.head())
        figure = model.plot(forecast)
        

        
ts=Time_Series("inventario.csv", periodo, forecast_days)    
    
ts.prophet()
