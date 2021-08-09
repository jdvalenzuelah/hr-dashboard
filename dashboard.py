import pandas as pd
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, DataTable, TableColumn, PreText
from bokeh.transform import factor_cmap, cumsum
from bokeh.plotting import figure
from bokeh.palettes import Spectral6, Category20c
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.core.properties import Seq, String
from math import pi

data = pd.read_excel('./data/db.xls')

vpu = data.loc[data['Vacante'] == True]\
    .groupby('Ubicación')\
    .count()[['Usuario']]\
    .sort_values('Usuario', ascending=False)\
    .reset_index()

source = ColumnDataSource(data=vpu.head(5))
fill_color=factor_cmap('Ubicación', palette=Spectral6, factors=sorted(vpu['Ubicación'].unique()))
vpup = figure(x_range=vpu['Ubicación'], plot_height=350, plot_width=900, title="Vacantes por ubicación")
vpup.vbar(x='Ubicación', top='Usuario', width=0.9, source=source, legend_field="Ubicación",
       line_color='white', fill_color=fill_color)

data['Tipo de jornada'] = data['Tipo de jornada'].apply(lambda x: x.strip() if type(x) == str else x)
data['Tipo de jornada'] = data['Tipo de jornada'].apply(lambda x: 'Ordinaria' if x == 'Ordinario' else x)

ept = data.loc[data['Estado del Empleado'] == 'Con terminación de contrato']\
    [['Estado del Empleado', 'Tipo de jornada']]\
    .groupby('Tipo de jornada')\
    .count()\
    .reset_index()\
    .sort_values('Estado del Empleado', ascending=False)

source = ColumnDataSource(data=ept)
fill_color=factor_cmap('Tipo de jornada', palette=Spectral6, factors=sorted(ept['Tipo de jornada'].unique()))
eptp = figure(x_range=ept['Tipo de jornada'], plot_height=350, plot_width=700, title="Empleados por jornada con terminación de contrato")
eptp.vbar(x='Tipo de jornada', top='Estado del Empleado', width=0.9, source=source, legend_field="Tipo de jornada",
       line_color='white', fill_color=fill_color)

epsu = data.loc[data['Pertenece a Sindicato'] == 'Si']\
    .groupby(['Pertenece a Sindicato', 'Ubicación'])\
    .count()[['Usuario']]\
    .reset_index()\
    .sort_values('Usuario', ascending=False)

source = ColumnDataSource(data=epsu)
fill_color=factor_cmap('Ubicación', palette=Spectral6, factors=sorted(epsu['Ubicación'].unique()))
epsup = figure(x_range=epsu['Ubicación'], plot_height=350, plot_width=900, title="Empleados que pertenecen a sindicato por ubicacion")
epsup.vbar(x='Ubicación', top='Usuario', width=0.9, source=source, legend_field="Ubicación",
       line_color='white', fill_color=fill_color)

data['Año Última Contratación'] = data['Fecha de Última Contratación'].apply(lambda x: x.year)

cp = data.groupby('Año Última Contratación')\
    .count()[['Usuario']]\
    .sort_values('Año Última Contratación')\
    .reset_index()
cp.head(5)

cpp = figure(title="Contrataciones por año", plot_height=350, plot_width=1000, x_axis_label="Año", y_axis_label="Contrataciones")
cpp.line(cp['Año Última Contratación'], cp['Usuario'], line_width=2)

cpu = data.loc[data['Vacante'] == False]\
    .groupby('Ubicación')\
    .count()\
    .reset_index()\
    [['Ubicación', 'Usuario']]

source = ColumnDataSource(data=cpu)
cpup = DataTable(
    source=source,
    columns=[
        TableColumn(field="Ubicación", title="Ubicación"),
        TableColumn(field="Usuario", title="Cantidad Contratados"),
    ],
    width=300,
    height=350,
)

tc = data.loc[data['Vacante'] == False]['Usuario'].count()
tcp = PreText(text=f'Total de contratados: {tc}', width=300)

cpd = data.groupby('Nombre Departamento')\
    .count()\
    .reset_index()\
    .sort_values('Usuario', ascending=False)\
    .head(20)\
    [['Nombre Departamento', 'Usuario']]
cpd['angle'] = cpd['Usuario']/cpd['Usuario'].sum() * 2*pi
cpd['color'] = Category20c[len(cpd)]
cpd['Departamento'] = cpd['Nombre Departamento']

cpdp = figure(plot_height=720, plot_width=900, title="20 Departamentos con mas empleados", tools="hover", tooltips="@Departamento: @Usuario", x_range=(-0.5, 1.0))

cpdp.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='Departamento', source=cpd)




sub_col = column(tcp, cpup)
row0 = row(sub_col, eptp)
col0 = column(row0, cpp)
col1 = column(cpdp)

row1 = row(col0, col1)
row2 = row(vpup, epsup)

layout = column(row1, row2)

output_file("index.html")
show(layout)