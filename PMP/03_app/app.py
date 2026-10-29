from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import folium
import plotly.graph_objects as go
from streamlit_folium import st_folium

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB = PROJECT_ROOT / '01_database' / 'pmp_atlas.sqlite'
EXPORTS = PROJECT_ROOT / '04_exports'

st.set_page_config(page_title='NITA AI | PMP Atlas', page_icon='🌧️', layout='wide', initial_sidebar_state='collapsed')
st.markdown('''<style>
.stApp{background:#f5f7f4;color:#0f172a}.block-container{max-width:none;width:100%;height:calc(100vh - 2.3rem);overflow-y:auto;overflow-x:hidden;padding:.18rem 1.15rem .65rem}[data-testid="stHeader"]{background:transparent;height:0}.main{overflow:hidden}.brand{color:#087f83;font-size:.63rem;font-weight:850;letter-spacing:.13em;text-transform:uppercase}.brand-mark{display:inline-flex;align-items:center;justify-content:center;width:1.15rem;height:1.15rem;margin-right:.32rem;border-radius:50%;background:#087f83;color:#fff;font-size:.6rem;font-weight:900;vertical-align:middle}.brand-sub{color:#64748b;font-size:.54rem;letter-spacing:.08em;text-transform:uppercase;margin-left:1.48rem;margin-top:-.12rem}.reference-header{background:#fff;border:1px solid #dbe2e8;border-radius:3px;padding:.42rem .55rem .48rem;margin:.42rem 0 .5rem}.reference-brand{color:#087f83;font-size:.62rem;font-weight:850;letter-spacing:.11em;text-transform:uppercase}.reference-title{color:#12324a;font-size:clamp(1.05rem,2vw,1.55rem);font-weight:700;line-height:1.08;letter-spacing:-.025em;margin:.13rem 0 .12rem}.reference-subtitle{color:#687786;font-size:.68rem;line-height:1.25}.report-badge{color:#087f83;font-size:.68rem;font-weight:800;margin-left:.45rem}.card-label{color:#5b6573;font-size:.65rem;font-weight:700}.card-title{font-size:1rem;font-weight:750;margin-top:.12rem}.section-title{font-size:1rem;font-weight:750;margin:.05rem 0 .12rem}.section-copy{color:#5b6573;font-size:.7rem;line-height:1.25}.status{border-left:3px solid #84cc16;background:#f0fdf4;padding:.45rem .6rem;border-radius:5px}.navline{color:#5b6573;font-size:.67rem;padding:0 0 .14rem;border-bottom:1px solid #dbe2e8}.nav-tab{display:inline-block;margin-right:1rem;color:#087f83;font-weight:700;border-bottom:2px solid #087f83;padding-bottom:.12rem}.nav-tab-muted{display:inline-block;color:#6b7280}.source-note{color:#6b7280;font-size:.62rem;margin-top:.15rem}div[data-testid="stMetric"]{background:#fff;border:1px solid #dbe2e8;border-radius:4px;padding:.15rem .35rem}
@media (max-width:900px){.block-container{padding-left:.7rem;padding-right:.7rem}.hero-title{font-size:1.9rem}.hero-copy{font-size:.72rem}.brand-sub{display:none}}
@media (max-width:640px){.block-container{height:calc(100vh - 2rem);padding:.25rem .45rem .6rem}.brand{font-size:.6rem}.brand-mark{width:1.25rem;height:1.25rem}.hero-title{font-size:1.55rem}.stMetric{font-size:.75rem}}
</style>''', unsafe_allow_html=True)

st.markdown('''<style>
:root{--navy:#102a43;--navy-2:#163f59;--teal:#087f83;--lime:#a8c83a;--ink:#102a43;--muted:#607487;--line:#d8e2e8;--canvas:#eef3f5}
.stApp{background:var(--canvas);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
.block-container{padding:.15rem 1.35rem .9rem;max-width:1600px;margin:0 auto}
.navline{background:var(--navy);color:#d9edf0;border:0;border-radius:0 0 8px 8px;padding:.38rem .75rem;margin:0 0 .65rem;font-size:.68rem;box-shadow:0 3px 12px rgba(16,42,67,.14)}
.nav-tab{color:#fff;border:0;padding:0;margin-right:1.25rem;letter-spacing:.04em}.nav-tab-muted{color:#9ec4cb}
.reference-header{position:relative;overflow:hidden;background:linear-gradient(110deg,var(--navy) 0%,#174c66 62%,#087f83 100%);border:0;border-radius:12px;padding:1rem 1.2rem 1.05rem;margin:.35rem 0 .7rem;box-shadow:0 8px 22px rgba(16,42,67,.15)}
.reference-header:after{content:"";position:absolute;right:-5rem;top:-6rem;width:18rem;height:18rem;border:28px solid rgba(168,200,58,.16);border-radius:50%}
.active-scope{background:#f4f8fa;border:1px solid var(--line);border-radius:8px;padding:.42rem .65rem;line-height:1.25}
.reference-brand{position:relative;z-index:1;color:#b8df69;font-size:.64rem;letter-spacing:.16em;font-weight:850}
.reference-title{position:relative;z-index:1;color:#fff;font-size:clamp(1.25rem,2.5vw,2rem);letter-spacing:-.035em;margin:.22rem 0 .2rem;font-weight:750}
.reference-subtitle{position:relative;z-index:1;color:#d7e9ed;font-size:.76rem;max-width:720px}.report-badge{color:#cde88e;border-left:1px solid rgba(255,255,255,.35);padding-left:.55rem}
[data-testid="stMetric"]{background:#fff!important;border:1px solid var(--line)!important;border-radius:9px!important;box-shadow:0 3px 10px rgba(16,42,67,.05);padding:.45rem .65rem!important}
[data-testid="stMetricLabel"]{color:#64798a!important;text-transform:uppercase;letter-spacing:.08em;font-size:.58rem!important;font-weight:800!important}[data-testid="stMetricValue"]{color:var(--navy)!important;font-size:1.22rem!important;font-weight:750!important}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--line)!important;border-radius:10px!important;box-shadow:0 3px 12px rgba(16,42,67,.04);background:rgba(255,255,255,.72)}
.section-title{color:var(--navy);font-size:1.03rem;font-weight:800;letter-spacing:-.01em}.section-copy{color:var(--muted);font-size:.72rem}
.card-label{color:var(--teal);font-size:.61rem;letter-spacing:.12em;text-transform:uppercase;font-weight:850}.card-title{color:var(--navy);font-size:1.02rem;font-weight:800}
.status{border-left:3px solid var(--lime);background:#f4f9e9;color:var(--navy);padding:.5rem .65rem;border-radius:7px}.source-note{color:#708696}
[data-baseweb="tab-list"]{gap:.3rem;border-bottom:1px solid var(--line);margin-bottom:.55rem}[data-baseweb="tab"]{height:2.2rem;color:#667c8b;font-size:.72rem;font-weight:750;padding:0 .85rem}[aria-selected="true"][data-baseweb="tab"]{color:var(--teal);border-bottom:3px solid var(--teal)}
div[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:8px;overflow:hidden}div[data-testid="stPlotlyChart"]{background:#fff;border:1px solid var(--line);border-radius:9px;padding:.2rem;box-shadow:0 3px 10px rgba(16,42,67,.04)}
iframe{border-radius:10px;border:1px solid var(--line)}
section[data-testid="stSidebar"]{background:#f7fafb;border-right:1px solid var(--line)}section[data-testid="stSidebar"] .block-container{padding:.9rem .8rem}section[data-testid="stSidebar"] h2{color:var(--navy);font-size:1rem}section[data-testid="stSidebar"] [data-testid="stRadio"] label{font-size:.76rem;color:#496273}
button[kind="secondary"]{border-color:#c7d8df;border-radius:7px;color:var(--navy)}
@media(max-width:900px){.block-container{padding-left:.65rem;padding-right:.65rem}.reference-header{padding:.8rem .9rem}.reference-title{font-size:1.3rem}}
</style>''', unsafe_allow_html=True)

@st.cache_resource
def conn(): return sqlite3.connect(DB, check_same_thread=False)

@st.cache_data
def query(sql, params=()): return pd.read_sql_query(sql, conn(), params=params)

def gumbel_screening(storm_df):
    """Fit a method-of-moments Gumbel curve to annual storm maxima.

    This is a regional screening estimate from the extracted storm catalogue,
    not a validated station frequency analysis. Station annual maxima are not
    present in the current source-derived database.
    """
    if storm_df.empty or storm_df['year'].nunique() < 3:
        return pd.DataFrame(), None, None
    annual = storm_df.dropna(subset=['year', 'peak_rainfall_mm']).groupby('year', as_index=False)['peak_rainfall_mm'].max()
    if len(annual) < 3:
        return annual, None, None
    values = annual['peak_rainfall_mm'].astype(float).to_numpy()
    mean = float(values.mean())
    std = float(values.std(ddof=1))
    beta = std * np.sqrt(6.0) / np.pi
    loc = mean - 0.5772156649 * beta
    periods = np.array([2, 5, 10, 25, 50, 100, 200, 500], dtype=float)
    quantiles = loc - beta * np.log(-np.log(1.0 - 1.0 / periods))
    rp = pd.DataFrame({'return_period_years': periods.astype(int), 'rainfall_mm': quantiles})
    return annual, (loc, beta), rp

def station_extreme_figure(station_df, title):
    fig=go.Figure(go.Bar(x=station_df['duration_hours'],y=station_df['rainfall_mm'],text=station_df['rainfall_mm'],marker_color='#087f83',texttemplate='%{text:.0f} mm',textposition='outside'))
    fig.update_layout(title=title,xaxis_title='Duration (hours)',yaxis_title='Observed extreme rainfall (mm)',height=285,margin=dict(l=15,r=15,t=42,b=15))
    return fig

def dad_figure(long, title):
    fig=go.Figure()
    for (series, duration_value), part in long.groupby(['series','duration_hours'], dropna=False):
        label=f'{series} · {int(duration_value)} h' if pd.notna(duration_value) else str(series)
        fig.add_trace(go.Scatter(x=part['area_km2'],y=part['value'],mode='lines+markers',name=label))
    fig.update_xaxes(type='log',title='Area (km², logarithmic scale)')
    fig.update_layout(title=title,yaxis_title='Depth (mm)',height=500,margin=dict(l=15,r=15,t=42,b=15),legend_title_text='Curve')
    return fig

def return_period_figure(rp, title):
    fig=go.Figure()
    for label,color in [('LL','#94a3b8'),('UL','#94a3b8'),('EST','#087f83')]:
        part=rp[rp['estimate_class'].eq(label)].sort_values('return_period_years')
        if not part.empty:
            fig.add_trace(go.Scatter(x=part['return_period_years'],y=part['rainfall_mm'],mode='lines+markers',name=label,line=dict(color=color,width=3 if label=='EST' else 1.5,dash='solid' if label=='EST' else 'dot')))
    fig.update_xaxes(type='log',title='Return period (years)',tickvals=[2.33,5,10,25,50,100,500,1000,5000,10000],ticktext=['2.33','5','10','25','50','100','500','1k','5k','10k'])
    fig.update_layout(title=title,yaxis_title='Rainfall depth (mm)',height=340,margin=dict(l=15,r=15,t=42,b=15))
    return fig

def esri_basemap():
    """Create an Esri ArcGIS basemap stack with topographic and satellite-hybrid options."""
    m = folium.Map(location=[22.4, 75.5], zoom_start=6, control_scale=True, prefer_canvas=True, tiles=None, scrollWheelZoom=False, zoom_control=True)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        name='ArcGIS World Topographic',
        attr='Tiles &copy; Esri — National Geographic, Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri Korea, Esri (Thailand), TomTom, 2012',
        overlay=False,
        control=True,
        max_zoom=19,
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        name='ArcGIS Satellite',
        attr='Tiles &copy; Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community',
        overlay=False,
        control=True,
        max_zoom=19,
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        name='ArcGIS Boundaries & Places',
        attr='Labels &copy; Esri',
        overlay=True,
        control=True,
        max_zoom=19,
    ).add_to(m)
    folium.LayerControl(collapsed=True, position='topright').add_to(m)
    return m

def render_hydrology_analytics(catchment, duration):
    st.markdown('<div class="section-title">Hydrology analytics workspace</div><div class="section-copy">Separate analytical tabs for station frequency, DAD/PMP curves and map context.</div>', unsafe_allow_html=True)
    frequency_tab, climatology_tab, dad_tab, map_tab = st.tabs(['Return periods & Gumbel', 'Station climatology', 'DAD / PMP curves', 'Station map'])
    station_sql='SELECT station_key,station_name,district_name,catchment_code FROM rainfall_station'
    station_params=[]
    if catchment!='All': station_sql+=' WHERE catchment_code=?'; station_params.append(catchment)
    station_options=query(station_sql+' ORDER BY station_name',station_params)
    grid_sql='SELECT DISTINCT grid_id FROM grid_pmp_estimate'
    grid_params=[]
    if catchment!='All': grid_sql+=' WHERE grid_id LIKE ?'; grid_params.append(f'%{catchment}%')
    grid_options=query(grid_sql+' ORDER BY grid_id',grid_params)['grid_id'].tolist()
    station_key=station_options['station_key'].iloc[0] if not station_options.empty else None
    station_name=station_options.loc[station_options['station_key'].eq(station_key),'station_name'].iloc[0] if station_key else 'Selected station'
    station_df=query('SELECT duration_hours,rainfall_mm,event_date_text FROM station_extreme_rainfall WHERE station_key=? ORDER BY duration_hours',[station_key]) if station_key else pd.DataFrame()
    with frequency_tab:
        a,b=st.columns([1.4,1])
        station_key=a.selectbox('Station',station_options['station_key'].tolist(),format_func=lambda k: station_options.loc[station_options['station_key'].eq(k),'station_name'].iloc[0],key='analytics_station') if not station_options.empty else None
        station_name=station_options.loc[station_options['station_key'].eq(station_key),'station_name'].iloc[0] if station_key else 'Selected station'
        station_df=query('SELECT duration_hours,rainfall_mm,event_date_text FROM station_extreme_rainfall WHERE station_key=? ORDER BY duration_hours',[station_key]) if station_key else pd.DataFrame()
        if not station_df.empty:
            fig=station_extreme_figure(station_df,f'{station_name}: observed station extremes')
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
        rp_sql='SELECT * FROM return_period_estimate WHERE station_key=?'
        rp_params=[station_key]
        if duration!='All': rp_sql+=' AND duration_hours=?'; rp_params.append(duration)
        rp=query(rp_sql+' ORDER BY duration_hours,return_period_years,estimate_class',rp_params) if station_key else pd.DataFrame()
        if not rp.empty:
            for dur, part in rp.groupby('duration_hours'):
                st.plotly_chart(return_period_figure(part,f'{station_name}: {int(dur)}-hour Gumbel return-period rainfall'),use_container_width=True,config={'displayModeBar':False})
            st.dataframe(rp[['duration_hours','parameter_xi','parameter_alpha','estimate_class','return_period_years','rainfall_mm','source_pdf_page']],use_container_width=True,hide_index=True,height=220)
            st.download_button('Download station return-period table',rp.to_csv(index=False).encode(),'station_return_periods.csv','text/csv')
        storm_sql='SELECT year,duration_hours,peak_rainfall_mm,storm_centre_name FROM rainfall_storm WHERE peak_rainfall_mm IS NOT NULL'
        storm_params=[]
        if duration!='All': storm_sql+=' AND duration_hours=?'; storm_params.append(duration)
        storm_df=query(storm_sql,storm_params)
        annual, params, rp = gumbel_screening(storm_df)
        if rp is not None:
            fig=go.Figure(go.Scatter(x=rp['return_period_years'],y=rp['rainfall_mm'],mode='lines+markers',name='Gumbel screening estimate',line=dict(color='#4d7c0f',width=3)))
            fig.update_xaxes(type='log',tickvals=[2,5,10,25,50,100,200,500],ticktext=['2','5','10','25','50','100','200','500'])
            fig.update_layout(title='Regional storm-catalogue Gumbel screening',xaxis_title='Return period (years)',yaxis_title='Rainfall depth (mm)',height=300,margin=dict(l=15,r=15,t=42,b=15))
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
            loc,beta=params
            m1,m2,m3=st.columns(3); m1.metric('Annual maxima used',f'{len(annual):,} years'); m2.metric('Gumbel location',f'{loc:.1f} mm'); m3.metric('Gumbel scale',f'{beta:.1f} mm')
            st.caption('Regional storm-catalogue screening is retained as a separate diagnostic. The station return-period tables above are source-extracted Gumbel estimates with EST/LL/UL rows.')
    with climatology_tab:
        clim=query('SELECT * FROM station_climatology WHERE station_key=?',[station_key]) if station_key else pd.DataFrame()
        if clim.empty:
            st.info('The selected station is outside the 647-station climatology table in Volume II; use the source atlas workspace for the complete station inventory.')
        else:
            c1,c2=st.columns(2)
            with c1:
                st.metric('Elevation',f"{clim.iloc[0]['elevation_m']:.0f} m" if pd.notna(clim.iloc[0]['elevation_m']) else 'Not reported')
                st.dataframe(clim[['record_period','years_of_record','monsoon_mean_mm','monsoon_stddev_mm','monsoon_cv_pct','annual_mean_mm','annual_stddev_mm','annual_cv_pct']],use_container_width=True,hide_index=True)
            with c2:
                vals=pd.DataFrame({'Statistic':['Monsoon mean','Annual mean','Monsoon SD','Annual SD'],'Rainfall (mm)':[clim.iloc[0]['monsoon_mean_mm'],clim.iloc[0]['annual_mean_mm'],clim.iloc[0]['monsoon_stddev_mm'],clim.iloc[0]['annual_stddev_mm']]})
                fig=go.Figure(go.Bar(x=vals['Statistic'],y=vals['Rainfall (mm)'],marker_color=['#087f83','#163f59','#84cc16','#a8c83a']))
                fig.update_layout(title='Station climatology summary',yaxis_title='Rainfall (mm)',height=270,margin=dict(l=15,r=15,t=42,b=15))
                st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
            st.caption(f"Source: Volume II: Maps and Tables, Table 1-1, PDF page {int(clim.iloc[0]['source_pdf_page'])}.")
    with dad_tab:
        grid_id=st.selectbox('DAD/PMP grid',grid_options) if grid_options else None
        if grid_id:
            dad=query('SELECT duration_hours,area_km2,grid_rain_depth_mm,sps_mm,mmf,pmp_mm,storm_date_text FROM grid_pmp_estimate WHERE grid_id=? ORDER BY duration_hours,area_km2',[grid_id])
            if duration!='All': dad=dad[dad['duration_hours'].eq(duration)]
            long=pd.concat([dad.assign(series='Grid rain depth',value=dad['grid_rain_depth_mm']),dad.assign(series='SPS',value=dad['sps_mm']),dad.assign(series='MMF',value=dad['mmf']),dad.assign(series='PMP',value=dad['pmp_mm'])],ignore_index=True).dropna(subset=['value'])
            fig=dad_figure(long,f'Depth–Area–Duration / PMP curves: {grid_id}')
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
            st.download_button('Download selected DAD curves',dad.to_csv(index=False).encode(),'dad_curves.csv','text/csv')
        st.markdown('#### Source DAD storm curves')
        dad_source=query('SELECT duration_hours,storm_serial_no,storm_date_text,storm_centre,peak_rainfall_mm,area_km2,depth_mm,source_pdf_page FROM dad_storm_value ORDER BY duration_hours,storm_serial_no,area_km2')
        if duration!='All': dad_source=dad_source[dad_source['duration_hours'].eq(duration)]
        st.caption(f'{len(dad_source):,} source-linked DAD points from Tables 3-3 to 3-5.')
        st.dataframe(dad_source,use_container_width=True,hide_index=True,height=260)
        st.download_button('Download source DAD points',dad_source.to_csv(index=False).encode(),'source_dad_points.csv','text/csv')
    with map_tab:
        m=esri_basemap()
        map_df=query('SELECT station_key,station_name,catchment_code,latitude_deg,longitude_deg FROM rainfall_station WHERE latitude_deg IS NOT NULL AND longitude_deg IS NOT NULL'+(' AND catchment_code=?' if catchment!='All' else ''),[catchment] if catchment!='All' else [])
        for r in map_df.itertuples(): folium.CircleMarker([r.latitude_deg,r.longitude_deg],radius=4,tooltip=f'{r.station_name} ({r.catchment_code})',color='#087f83',fill=True,fill_opacity=.8).add_to(m)
        st_folium(m,height=650,width=1400,use_container_width=True)

if not DB.exists():
    st.error('Database not found. Run the ETL: python .\\02_etl\\etl.py')
    st.stop()

st.markdown('<div class="navline"><span class="nav-tab">Flood &amp; Hydrology</span><span class="nav-tab-muted">PMP Atlas</span></div>', unsafe_allow_html=True)
st.markdown('<div class="reference-header"><div class="reference-brand">● NITA AI</div><div class="reference-title">Narmada Basin PMP Atlas <span class="report-badge">Report V1</span></div><div class="reference-subtitle">NITA AI dashboard for station extremes, rainfall storms, PMP grids and GIS-based hydrological analysis</div></div>', unsafe_allow_html=True)

counts={'Stations':int(query('SELECT COUNT(*) n FROM rainfall_station').iloc[0,0]),'Return-period rows':int(query('SELECT COUNT(*) n FROM return_period_estimate').iloc[0,0]),'DAD points':int(query('SELECT COUNT(*) n FROM dad_storm_value').iloc[0,0]),'Source assets':int(query('SELECT COUNT(*) n FROM source_asset_registry').iloc[0,0])}
cols=st.columns(4)
for col,(label,value) in zip(cols,counts.items()): col.metric(label,f'{value:,}')

with st.container(border=True):
    st.markdown('<div class="card-label">Atlas workspace</div>',unsafe_allow_html=True)
    control1,control2,control3=st.columns([1.5,1.2,2.5],gap='small')
    view=control1.selectbox('Workspace',['Station extremes','Hydrology analytics','Station climatology','Return-period rainfall','DAD storm evidence','Grid PMP','Storm catalogue','Source atlas','NITA exports'],label_visibility='collapsed')
    with control2:
        with st.popover('Filter data'):
            st.markdown('### Filter data')
            st.caption('Filters apply to the active workspace table and map.')
            catchments=['All']+query('SELECT catchment_code FROM catchment ORDER BY catchment_code')['catchment_code'].tolist()
            catchment=st.selectbox('Catchment',catchments)
            duration=st.selectbox('Duration',['All',24,48,72],format_func=lambda x:'All durations' if x=='All' else f'{x}-hour duration')
            if view=='Station extremes':
                station_text=st.text_input('Station name contains',placeholder='e.g. Abu')
                district_options=['All']+query('SELECT DISTINCT district_name FROM rainfall_station WHERE district_name IS NOT NULL ORDER BY district_name')['district_name'].tolist()
                district_filter=st.selectbox('District',district_options)
                type_options=['All']+query('SELECT DISTINCT station_type FROM rainfall_station WHERE station_type IS NOT NULL ORDER BY station_type')['station_type'].tolist()
                station_type_filter=st.selectbox('Station type',type_options)
                min_rainfall=st.number_input('Minimum rainfall (mm)',min_value=0.0,value=0.0,step=10.0)
            elif view=='Grid PMP':
                grid_text=st.text_input('Grid ID contains',placeholder='e.g. 103L')
                min_area=st.number_input('Minimum area (km²)',min_value=0.0,value=0.0,step=25.0)
                max_area=st.number_input('Maximum area (km²)',min_value=0.0,value=0.0,step=100.0)
                min_pmp=st.number_input('Minimum PMP (mm)',min_value=0.0,value=0.0,step=25.0)
            elif view=='Storm catalogue':
                centre_text=st.text_input('Storm centre contains',placeholder='e.g. Surat')
                min_peak=st.number_input('Minimum peak rainfall (mm)',min_value=0.0,value=0.0,step=25.0)
                year_min=st.number_input('From year',min_value=1800,max_value=2100,value=1800,step=1)
                year_max=st.number_input('To year',min_value=1800,max_value=2100,value=2100,step=1)
    control3.markdown(f'<div class="active-scope"><span class="card-label">Active scope</span><br><strong>{catchment if catchment!="All" else "All atlas systems"}</strong><br><span class="section-copy">{("All durations" if duration=="All" else str(duration)+"-hour products")}</span></div>',unsafe_allow_html=True)

station_map=None
with st.container():
    if view=='Station extremes':
        sql='''SELECT s.station_key,s.catchment_code,s.district_name,s.station_name,s.station_type,s.latitude_deg,s.longitude_deg,s.data_length_years,e.duration_hours,e.rainfall_mm,e.event_date_text,e.source_provenance_id FROM rainfall_station s JOIN station_extreme_rainfall e USING(station_key) WHERE 1=1'''; params=[]
        if catchment!='All': sql+=' AND s.catchment_code=?'; params.append(catchment)
        if duration!='All': sql+=' AND e.duration_hours=?'; params.append(duration)
        sql+=' ORDER BY s.catchment_code,s.serial_no,e.duration_hours'; df=query(sql,params)
        if station_text: df=df[df['station_name'].fillna('').str.contains(station_text,case=False,na=False)]
        if district_filter!='All': df=df[df['district_name'].eq(district_filter)]
        if station_type_filter!='All': df=df[df['station_type'].eq(station_type_filter)]
        if min_rainfall>0: df=df[df['rainfall_mm'].ge(min_rainfall)]
        st.caption(f'{len(df):,} station records match the active filters.')
        st.markdown('<div class="section-title">Station extremes and rainfall evidence</div><div class="section-copy">Observed maximum 1-, 2- and 3-day rainfall records linked to the atlas station inventory.</div>',unsafe_allow_html=True)
        m=esri_basemap()
        for r in df.drop_duplicates('station_key').itertuples():
            if pd.notna(r.latitude_deg) and pd.notna(r.longitude_deg): folium.CircleMarker([r.latitude_deg,r.longitude_deg],radius=4,tooltip=f'{r.station_name} ({r.catchment_code})',color='#087f83',fill=True,fill_opacity=.8).add_to(m)
        station_map=m
        table_col,map_col=st.columns([1.35,1],gap='small')
        with table_col:
            st.dataframe(df,use_container_width=True,hide_index=True,height=600)
        with map_col:
            st.markdown('<div class="card-label">Geographic station context</div>',unsafe_allow_html=True)
            st_folium(m,height=600,width=1400,use_container_width=True)
        st.download_button('Download filtered CSV',df.to_csv(index=False).encode(),'station_extremes_filtered.csv','text/csv')
    elif view=='Hydrology analytics':
        render_hydrology_analytics(catchment, duration)
    elif False and view=='Hydrology analytics':
        st.markdown('<div class="section-title">Station storm frequency and DAD analysis</div><div class="section-copy">Interactive screening charts for the selected station, regional storm catalogue and PMP depth–area–duration products.</div>',unsafe_allow_html=True)
        station_sql='SELECT station_key,station_name,district_name,catchment_code FROM rainfall_station'
        station_params=[]
        if catchment!='All': station_sql+=' WHERE catchment_code=?'; station_params.append(catchment)
        station_options=query(station_sql+' ORDER BY station_name',station_params)
        grid_sql='SELECT DISTINCT grid_id FROM grid_pmp_estimate'
        grid_params=[]
        if catchment!='All': grid_sql+=' WHERE grid_id LIKE ?'; grid_params.append(f'%{catchment}%')
        grid_options=query(grid_sql+' ORDER BY grid_id',grid_params)['grid_id'].tolist()
        a,b=st.columns([1.4,1])
        station_key=a.selectbox('Station',station_options['station_key'].tolist(),format_func=lambda k: station_options.loc[station_options['station_key'].eq(k),'station_name'].iloc[0] if not station_options.empty else k)
        grid_id=b.selectbox('DAD/PMP grid',grid_options) if grid_options else None

        station_name=station_options.loc[station_options['station_key'].eq(station_key),'station_name'].iloc[0] if station_key else 'Selected station'
        station_df=query('SELECT duration_hours,rainfall_mm,event_date_text FROM station_extreme_rainfall WHERE station_key=? ORDER BY duration_hours',[station_key]) if station_key else pd.DataFrame()
        if not station_df.empty:
            c1,c2=st.columns(2)
            with c1:
                fig=station_extreme_figure(station_df,f'{station_name}: observed station extremes')
                st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
            with c2:
                st.markdown('<div class="status"><strong>Frequency-analysis status</strong><br><span class="section-copy">Station annual-maxima series and persisted Gumbel parameters are not yet available in the extracted atlas tables. The return-period chart below is therefore regional storm-catalogue screening only, not a station design-frequency result.</span></div>',unsafe_allow_html=True)
                st.dataframe(station_df.rename(columns={'duration_hours':'Duration (h)','rainfall_mm':'Rainfall (mm)','event_date_text':'Atlas event date'}),use_container_width=True,hide_index=True,height=135)

        storm_sql='SELECT year,duration_hours,peak_rainfall_mm,storm_centre_name FROM rainfall_storm WHERE peak_rainfall_mm IS NOT NULL'
        storm_params=[]
        if duration!='All': storm_sql+=' AND duration_hours=?'; storm_params.append(duration)
        storm_df=query(storm_sql,storm_params)
        annual, params, rp = gumbel_screening(storm_df)
        if rp is not None:
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=rp['return_period_years'],y=rp['rainfall_mm'],mode='lines+markers',name='Gumbel screening estimate',line=dict(color='#4d7c0f',width=3)))
            if not station_df.empty and duration!='All':
                selected=station_df.loc[station_df['duration_hours'].eq(duration)]
                if not selected.empty:
                    fig.add_hline(y=float(selected.iloc[0]['rainfall_mm']),line_dash='dot',line_color='#087f83',annotation_text=f'{station_name} observed {duration}h extreme',annotation_position='top left')
            fig.update_xaxes(type='log',tickvals=[2,5,10,25,50,100,200,500],ticktext=['2','5','10','25','50','100','200','500'])
            fig.update_layout(title='Regional storm-catalogue Gumbel screening by return period',xaxis_title='Return period (years, logarithmic scale)',yaxis_title='Rainfall depth (mm)',height=300,margin=dict(l=15,r=15,t=42,b=15))
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
            loc,beta=params
            m1,m2,m3=st.columns(3); m1.metric('Annual maxima used',f'{len(annual):,} years'); m2.metric('Gumbel location',f'{loc:.1f} mm'); m3.metric('Gumbel scale',f'{beta:.1f} mm')
            st.caption('Method of moments: β = s√6/π and μ = x̄ − 0.5772β. Values are screening estimates from the extracted storm catalogue and require hydrologist review before model use.')
        if grid_id:
            dad=query('SELECT duration_hours,area_km2,grid_rain_depth_mm,sps_mm,mmf,pmp_mm,storm_date_text FROM grid_pmp_estimate WHERE grid_id=? ORDER BY duration_hours,area_km2',[grid_id])
            if duration!='All': dad=dad[dad['duration_hours'].eq(duration)]
            if not dad.empty:
                long=pd.concat([dad.assign(series='Grid rain depth',value=dad['grid_rain_depth_mm']),dad.assign(series='SPS',value=dad['sps_mm']),dad.assign(series='MMF',value=dad['mmf']),dad.assign(series='PMP',value=dad['pmp_mm'])],ignore_index=True)
                long=long.dropna(subset=['value'])
                fig=dad_figure(long,f'Depth–Area–Duration / PMP curves: {grid_id}')
                st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
                st.download_button('Download selected DAD curves',dad.to_csv(index=False).encode(),'dad_curves.csv','text/csv')
    elif view=='Grid PMP':
        sql='SELECT * FROM grid_pmp_estimate WHERE 1=1'; params=[]
        if duration!='All': sql+=' AND duration_hours=?'; params.append(duration)
        if catchment!='All': sql+=' AND grid_id LIKE ?'; params.append(f'%{catchment}%')
        sql+=' ORDER BY grid_id,duration_hours,area_km2'; df=query(sql,params)
        if grid_text: df=df[df['grid_id'].fillna('').str.contains(grid_text,case=False,na=False)]
        if min_area>0: df=df[df['area_km2'].ge(min_area)]
        if max_area>0: df=df[df['area_km2'].le(max_area)]
        if min_pmp>0: df=df[df['pmp_mm'].fillna(0).ge(min_pmp)]
        st.caption(f'{len(df):,} grid PMP records match the active filters.')
        st.markdown('<div class="section-title">Grid-wise PMP estimates</div><div class="section-copy">Depth-area-duration values with contributing storm, TAF, SPS, MMF and PMP fields.</div>',unsafe_allow_html=True)
        st.dataframe(df,use_container_width=True,hide_index=True,height=360); st.download_button('Download filtered CSV',df.to_csv(index=False).encode(),'grid_pmp_filtered.csv','text/csv')
    elif view=='Storm catalogue':
        sql='SELECT * FROM rainfall_storm WHERE 1=1'; params=[]
        if duration!='All': sql+=' AND duration_hours=?'; params.append(duration)
        sql+=' ORDER BY year,serial_no'; df=query(sql,params)
        if centre_text: df=df[df['storm_centre_name'].fillna('').str.contains(centre_text,case=False,na=False)]
        df=df[df['year'].fillna(0).between(year_min,year_max)]
        if min_peak>0: df=df[df['peak_rainfall_mm'].fillna(0).ge(min_peak)]
        st.caption(f'{len(df):,} storm records match the active filters.')
        st.markdown('<div class="section-title">Historical rainstorm catalogue</div><div class="section-copy">Storm-centre, duration and peak-rainfall records available for scenario construction.</div>',unsafe_allow_html=True)
        st.dataframe(df,use_container_width=True,hide_index=True,height=360); st.download_button('Download CSV',df.to_csv(index=False).encode(),'storms.csv','text/csv')
    elif view=='Station climatology':
        sql='SELECT * FROM station_climatology WHERE 1=1'; params=[]
        if catchment!='All': sql+=' AND catchment_code=?'; params.append(catchment)
        sql+=' ORDER BY catchment_code,serial_no'; df=query(sql,params)
        st.caption(f'{len(df):,} station climatology records from Volume II: Maps and Tables, Table 1-1.')
        st.markdown('<div class="section-title">Station climatology and record metadata</div><div class="section-copy">Monsoon and annual mean rainfall, standard deviation, coefficient of variation, elevation and record period.</div>',unsafe_allow_html=True)
        st.dataframe(df,use_container_width=True,hide_index=True,height=600); st.download_button('Download climatology CSV',df.to_csv(index=False).encode(),'station_climatology.csv','text/csv')
    elif view=='Return-period rainfall':
        sql='SELECT * FROM return_period_estimate WHERE 1=1'; params=[]
        if catchment!='All': sql+=' AND catchment_code=?'; params.append(catchment)
        if duration!='All': sql+=' AND duration_hours=?'; params.append(duration)
        sql+=' ORDER BY catchment_code,serial_no,duration_hours,return_period_years,estimate_class'; df=query(sql,params)
        st.caption(f'{len(df):,} source-linked Gumbel return-period rows with estimate, lower and upper confidence limits.')
        st.markdown('<div class="section-title">Return-period rainfall and Gumbel parameters</div><div class="section-copy">Station-wise 2.33- to 10,000-year rainfall estimates with the atlas xi/alpha parameters and 95% confidence-limit rows.</div>',unsafe_allow_html=True)
        st.dataframe(df,use_container_width=True,hide_index=True,height=600); st.download_button('Download return-period CSV',df.to_csv(index=False).encode(),'return_period_rainfall.csv','text/csv')
    elif view=='DAD storm evidence':
        sql='SELECT * FROM dad_storm_value WHERE 1=1'; params=[]
        if duration!='All': sql+=' AND duration_hours=?'; params.append(duration)
        sql+=' ORDER BY duration_hours,storm_serial_no,area_km2'; df=query(sql,params)
        st.caption(f'{len(df):,} source-linked DAD points from the three duration tables.')
        st.markdown('<div class="section-title">Depth-Area-Duration storm evidence</div><div class="section-copy">Source DAD values for the historical rainstorm catalogue, retained by duration, storm, standard area and PDF page.</div>',unsafe_allow_html=True)
        st.dataframe(df,use_container_width=True,hide_index=True,height=600); st.download_button('Download DAD evidence CSV',df.to_csv(index=False).encode(),'dad_storm_evidence.csv','text/csv')
    elif view=='Source atlas':
        st.markdown('<div class="section-title">Source atlas library</div><div class="section-copy">Page-level source retrieval, figure/table registry and raw extracted evidence for both immutable PMP Atlas volumes.</div>',unsafe_allow_html=True)
        p1,p2=st.columns(2)
        p1.metric('Indexed PDF pages',f"{int(query('SELECT COUNT(*) n FROM source_page_catalog').iloc[0,0]):,}")
        p2.metric('Registered figures/tables/maps',f"{int(query('SELECT COUNT(*) n FROM source_asset_registry').iloc[0,0]):,}")
        role=query('SELECT page_role,COUNT(*) AS pages FROM source_page_catalog GROUP BY page_role ORDER BY pages DESC')
        st.dataframe(role,use_container_width=True,hide_index=True,height=150)
        assets=query('SELECT document_key,pdf_page_number,asset_type,asset_label,asset_title,notes FROM source_asset_registry ORDER BY document_key,pdf_page_number')
        st.dataframe(assets,use_container_width=True,hide_index=True,height=320)
        st.download_button('Download source asset registry',assets.to_csv(index=False).encode(),'source_asset_registry.csv','text/csv')
        pages=query('SELECT document_key,pdf_page_number,volume_label,page_role,page_title FROM source_page_catalog ORDER BY document_key,pdf_page_number')
        st.download_button('Download page catalogue',pages.to_csv(index=False).encode(),'source_page_catalog.csv','text/csv')
    else:
        st.markdown('<div class="section-title">NITA-compatible export package</div><div class="section-copy">Downloadable outputs generated from the canonical database for map and modelling workflows.</div>',unsafe_allow_html=True)
        for p in sorted(EXPORTS.glob('*')):
            if p.is_file():
                with st.container(border=True):
                    a,b=st.columns([2,1]); a.markdown(f'**{p.name}**<br><span class="source-note">{p.stat().st_size:,} bytes</span>',unsafe_allow_html=True); b.download_button('Download',p.read_bytes(),p.name,key=p.name)

st.divider()
st.markdown('<div class="section-title">Project and integration status</div>', unsafe_allow_html=True)
status1,status2,status3=st.columns(3,gap='small')
with status1:
    with st.container(border=True):
        st.markdown('<div class="card-label">Project status</div><div class="card-title">Atlas coverage expanded</div><div class="section-copy">Both volumes are indexed with source-linked station climatology, return periods, DAD evidence, raw tables and map/figure references. Digitized spatial products and time/area curves remain explicitly identified for controlled digitization.</div>',unsafe_allow_html=True)
with status2:
    with st.container(border=True):
        st.markdown('<div class="card-label">Provenance</div><div class="card-title">Source-linked</div><div class="section-copy">Every extracted record carries a source page, table label, extraction run and validation status.</div>',unsafe_allow_html=True)
with status3:
    with st.container(border=True):
        st.markdown('<div class="card-label">NITA handoff</div><div class="card-title">Adapter-ready</div><div class="section-copy">The canonical schema is independent of upload format; exports can target GeoJSON, CSV, NetCDF, COG GeoTIFF or service URLs.</div>',unsafe_allow_html=True)
