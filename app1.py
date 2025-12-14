import streamlit as st
import random
import math
import statistics
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Simulasi Antrian Tiket Wahana",
    page_icon="🎢",
    layout="wide"
)

class TicketQueueSimulation:
    def __init__(self, arrival_times, service_time_mean=15, theme_park_mode=True):
        self.arrival_rates = [1/t for t in arrival_times]
        self.service_rate = 1 / service_time_mean
        self.service_time_mean = service_time_mean
        self.theme_park_mode = theme_park_mode
        
        self.ride_names = [
            "Roller Coaster Extreme", 
            "Ferris Wheel Raksasa", 
            "Rumah Hantu", 
            "Water Slide", 
            "Carousel", 
            "Boom Boom Car", 
            "Sky Tower", 
            "Poci-poci Berputar", 
            "Komedi Putar", 
            "Istana Balon"
        ]
        
        self.arrivals = []
        self.events = []
        self.queue_history = []
        self.server_busy_history = []
    
    def exponential_random(self, rate):
        return -math.log(1.0 - random.random()) / rate
    
    def generate_arrivals(self, num_customers=5):
        arrival_times = []
        current_time = 0
        
        for i in range(num_customers):
            rate = self.arrival_rates[i % len(self.arrival_rates)]
            inter_arrival = self.exponential_random(rate)
            current_time += inter_arrival
            
            ride = random.choice(self.ride_names) if self.theme_park_mode else "Wahana"
            
            arrival_times.append({
                'customer': i + 1,
                'arrival_time': current_time,
                'inter_arrival': inter_arrival,
                'arrival_rate': rate,
                'ride': ride
            })
        
        return arrival_times
    
    def simulate(self, num_events=3):
        self.arrivals = self.generate_arrivals(5)
        
        time = 0
        server_busy = False
        queue = []
        customers_in_system = 0
        server_busy_time = 0
        last_event_time = 0
        
        event_count = 0
        customer_time_data = []
        previous_time = 0
        previous_customers = 0
        
        event_list = [(a['arrival_time'], 'arrival', a['customer']) for a in self.arrivals]
        event_list.sort(key=lambda x: x[0])
        
        events_log = []
        
        self.queue_history.append((0, len(queue), customers_in_system, server_busy))
        self.server_busy_history.append((0, server_busy))
        
        while event_list and event_count < num_events:
            event_time, event_type, customer = event_list.pop(0)
            
            time_elapsed = event_time - last_event_time
            if server_busy:
                server_busy_time += time_elapsed
            
            customer_time_data.append({
                'time': event_time,
                'customers': previous_customers,
                'duration': event_time - previous_time
            })
            
            time = event_time
            last_event_time = time
            previous_time = time
            
            if event_type == 'arrival':
                customers_in_system += 1
                previous_customers = customers_in_system
                
                if not server_busy:
                    server_busy = True
                    service_time = self.exponential_random(self.service_rate)
                    departure_time = time + service_time
                    event_list.append((departure_time, 'departure', customer))
                    event_list.sort(key=lambda x: x[0])
                else:
                    queue.append(customer)
                
                events_log.append({
                    'sequence': event_count + 1,
                    'type': 'Kedatangan',
                    'customer': customer,
                    'time': time,
                    'in_system': customers_in_system,
                    'queue_length': len(queue),
                    'server_status': 'Sibuk' if server_busy else 'Idle'
                })
                
            elif event_type == 'departure':
                customers_in_system -= 1
                previous_customers = customers_in_system
                
                if queue:
                    next_customer = queue.pop(0)
                    service_time = self.exponential_random(self.service_rate)
                    departure_time = time + service_time
                    event_list.append((departure_time, 'departure', next_customer))
                    event_list.sort(key=lambda x: x[0])
                else:
                    server_busy = False
                
                events_log.append({
                    'sequence': event_count + 1,
                    'type': 'Keberangkatan',
                    'customer': customer,
                    'time': time,
                    'in_system': customers_in_system,
                    'queue_length': len(queue),
                    'server_status': 'Sibuk' if server_busy else 'Idle'
                })
            
            self.queue_history.append((time, len(queue), customers_in_system, server_busy))
            self.server_busy_history.append((time, server_busy))
            
            event_count += 1
        
        total_time = time
        
        utilization = server_busy_time / total_time if total_time > 0 else 0
        
        total_customer_time = 0
        for data in customer_time_data:
            total_customer_time += data['customers'] * data['duration']
        
        if total_time > previous_time:
            total_customer_time += previous_customers * (total_time - previous_time)
        
        avg_customers_in_system = total_customer_time / total_time if total_time > 0 else 0
        
        self.events = events_log
        
        return {
            'total_time': total_time,
            'server_utilization': utilization,
            'avg_customers_in_system': avg_customers_in_system,
            'final_customers_in_system': customers_in_system,
            'final_queue_length': len(queue),
            'server_busy': server_busy
        }

def plot_results(sim, results):
    """Buat visualisasi hasil simulasi"""
    if not sim.queue_history:
        return None
    
    times = [t[0] for t in sim.queue_history]
    queue_lengths = [t[1] for t in sim.queue_history]
    system_customers = [t[2] for t in sim.queue_history]
    server_status = [1 if t[3] else 0 for t in sim.queue_history]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('Visualisasi Hasil Simulasi Antrian Tiket Wahana', fontsize=14, fontweight='bold')
    
    # Plot 1: Panjang antrian vs waktu
    ax1 = axes[0, 0]
    ax1.step(times, queue_lengths, where='post', linewidth=2, color='royalblue')
    ax1.fill_between(times, queue_lengths, alpha=0.3, color='royalblue')
    ax1.set_xlabel('Waktu (menit)')
    ax1.set_ylabel('Panjang Antrian')
    ax1.set_title('Panjang Antrian vs Waktu')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Jumlah pengunjung dalam sistem vs waktu
    ax2 = axes[0, 1]
    ax2.step(times, system_customers, where='post', linewidth=2, color='coral')
    ax2.fill_between(times, system_customers, alpha=0.3, color='coral')
    ax2.set_xlabel('Waktu (menit)')
    ax2.set_ylabel('Jumlah Pengunjung dalam Sistem')
    ax2.set_title('Jumlah Pengunjung dalam Sistem vs Waktu')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Status loket vs waktu
    ax3 = axes[1, 0]
    ax3.step(times, server_status, where='post', linewidth=2, color='seagreen')
    ax3.set_xlabel('Waktu (menit)')
    ax3.set_ylabel('Status Loket')
    ax3.set_title('Status Loket vs Waktu')
    ax3.set_yticks([0, 1])
    ax3.set_yticklabels(['Idle', 'Sibuk'])
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Statistik sistem
    ax4 = axes[1, 1]
    stats_labels = ['Utilization', 'Avg Customers', 'Final Queue', 'Final in System']
    stats_values = [
        results['server_utilization'] * 100,
        results['avg_customers_in_system'],
        results['final_queue_length'],
        results['final_customers_in_system']
    ]
    
    colors = ['gold', 'lightcoral', 'lightblue', 'lightgreen']
    bars = ax4.bar(stats_labels, stats_values, color=colors)
    ax4.set_ylabel('Nilai')
    ax4.set_title('Statistik Sistem')
    ax4.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, stats_values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{val:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    return fig

def main():
    # Header aplikasi
    st.title("🎢 Sistem Simulasi Antrian Tiket Wahana")
    st.markdown("---")
    
    # Sidebar untuk parameter input
    with st.sidebar:
        st.header("⚙️ Parameter Simulasi")
        
        # Mode simulasi
        simulation_mode = st.radio(
            "Pilih Mode Simulasi:",
            ["Default", "Custom"]
        )
        
        if simulation_mode == "Default":
            arrival_times = [10, 12, 8, 15, 20]
            service_time_mean = 15
            num_events = 3
            theme_park_mode = True
            
            st.info("Parameter Default:")
            st.write(f"- Waktu antar kedatangan: {arrival_times}")
            st.write(f"- Rata-rata waktu pelayanan: {service_time_mean} menit")
            st.write(f"- Jumlah event: {num_events}")
            
        else:
            st.subheader("Parameter Custom")
            
            service_time_mean = st.number_input(
                "Rata-rata waktu pelayanan (menit):",
                min_value=1.0,
                max_value=60.0,
                value=15.0,
                step=0.5
            )
            
            st.subheader("Waktu antar kedatangan (menit):")
            col1, col2 = st.columns(2)
            with col1:
                arrival1 = st.number_input("Pengunjung 1:", min_value=1.0, value=10.0, step=0.5)
                arrival3 = st.number_input("Pengunjung 3:", min_value=1.0, value=8.0, step=0.5)
                arrival5 = st.number_input("Pengunjung 5:", min_value=1.0, value=20.0, step=0.5)
            with col2:
                arrival2 = st.number_input("Pengunjung 2:", min_value=1.0, value=12.0, step=0.5)
                arrival4 = st.number_input("Pengunjung 4:", min_value=1.0, value=15.0, step=0.5)
            
            arrival_times = [arrival1, arrival2, arrival3, arrival4, arrival5]
            
            num_events = st.slider(
                "Jumlah event yang disimulasikan:",
                min_value=1,
                max_value=10,
                value=3
            )
            
            theme_park_mode = st.checkbox("Mode Taman Hiburan", value=True)
        
        # Seed untuk reproducibility
        seed_value = st.number_input("Random Seed:", value=42, step=1)
        
        # Tombol jalankan simulasi
        run_simulation = st.button("🚀 Jalankan Simulasi", type="primary", use_container_width=True)
    
    # Main content area
    if run_simulation:
        random.seed(seed_value)
        
        # Jalankan simulasi
        sim = TicketQueueSimulation(
            arrival_times=arrival_times,
            service_time_mean=service_time_mean,
            theme_park_mode=theme_park_mode
        )
        
        results = sim.simulate(num_events=num_events)
        
        # Tampilkan hasil
        st.header("📊 Hasil Simulasi")
        
        # Bagian 1: Pola Kedatangan
        st.subheader("1. Pola Kedatangan 5 Pengunjung Pertama")
        
        arrival_data = []
        for arrival in sim.arrivals:
            arrival_data.append([
                arrival['customer'],
                round(1/arrival['arrival_rate'], 2),
                round(arrival['inter_arrival'], 2),
                round(arrival['arrival_time'], 2),
                arrival['ride'] if sim.theme_park_mode else "-"
            ])
        
        arrival_df = pd.DataFrame(
            arrival_data,
            columns=['Pengunjung', 'Rata-rata Waktu Antar (menit)', 'Waktu Antar Aktual', 
                     'Waktu Kedatangan', 'Wahana Tujuan']
        )
        
        st.dataframe(arrival_df, use_container_width=True)
        
        # Bagian 2: Event Simulasi
        st.subheader(f"2. Simulasi Sistem ({len(sim.events)} Event)")
        
        events_data = []
        for event in sim.events:
            events_data.append([
                event['sequence'],
                event['type'],
                event['customer'],
                round(event['time'], 2),
                event['in_system'],
                event['queue_length'],
                event['server_status']
            ])
        
        events_df = pd.DataFrame(
            events_data,
            columns=['#', 'Event', 'Pengunjung', 'Waktu', 'Dalam Sistem', 'Panjang Antrian', 'Status Loket']
        )
        
        st.dataframe(events_df, use_container_width=True)
        
        # Bagian 3: Statistik Sistem
        st.subheader("3. Statistik Sistem Antrian")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total waktu simulasi", f"{results['total_time']:.2f} menit")
            st.metric("Tingkat kesibukan loket", f"{results['server_utilization']:.2%}")
        
        with col2:
            st.metric("Rata-rata pengunjung dalam sistem", f"{results['avg_customers_in_system']:.2f}")
            st.metric("Pengunjung dalam sistem (akhir)", f"{results['final_customers_in_system']}")
        
        with col3:
            st.metric("Panjang antrian (akhir)", f"{results['final_queue_length']}")
            status_text = "Sibuk" if results['server_busy'] else "Idle"
            status_color = "inverse" if results['server_busy'] else "normal"
            st.metric("Status loket (akhir)", status_text)
        
        # Bagian 4: Perhitungan Teoritis
        st.subheader("4. Perhitungan Teoritis (M/M/1)")
        
        avg_arrival_rate = statistics.mean(sim.arrival_rates)
        rho = avg_arrival_rate / sim.service_rate
        
        if rho < 1:
            L = rho / (1 - rho)
            W = L / avg_arrival_rate
            Wq = rho * W
            
            teo_col1, teo_col2, teo_col3 = st.columns(3)
            
            with teo_col1:
                st.metric("Laju kedatangan rata-rata (λ)", f"{avg_arrival_rate:.4f}/menit")
                st.metric("Laju pelayanan (μ)", f"{sim.service_rate:.4f}/menit")
            
            with teo_col2:
                st.metric("Tingkat kesibukan teoritis (ρ)", f"{rho:.2%}")
                st.metric("Rata-rata pengunjung dalam sistem (L)", f"{L:.2f}")
            
            with teo_col3:
                st.metric("Rata-rata waktu dalam sistem (W)", f"{W:.2f} menit")
                st.metric("Rata-rata waktu menunggu (Wq)", f"{Wq:.2f} menit")
        else:
            st.warning(f"Sistem tidak stabil (ρ = {rho:.2%} ≥ 1)")
        
        # Bagian 5: Visualisasi
        st.subheader("5. Visualisasi Hasil")
        
        fig = plot_results(sim, results)
        if fig:
            st.pyplot(fig)
        
        # Bagian 6: Informasi Rumus
        with st.expander("📝 Rumus yang Digunakan"):
            st.markdown("""
            **Distribusi Eksponensial:**
            ```
            t = -ln(1 - U) / λ
            ```
            
            **Tingkat kesibukan (ρ):**
            ```
            ρ = waktu sibuk / total waktu
            ```
            
            **Rata-rata pengunjung dalam sistem:**
            ```
            L = ∫L(t)dt / total waktu
            ```
            
            **Untuk sistem M/M/1:**
            ```
            ρ = λ / μ
            L = ρ / (1 - ρ)
            W = L / λ
            Wq = ρ * W
            ```
            """)
        
        # Bagian 7: Download hasil
        st.subheader("6. Download Hasil")
        
        # Format hasil untuk download
        result_text = f"""LAPORAN SIMULASI ANTRIAN TIKET WAHANA
{'=' * 50}

PARAMETER SIMULASI:
• Rata-rata waktu pelayanan: {service_time_mean} menit
• Waktu antar kedatangan: {arrival_times} menit
• Mode Taman Hiburan: {'Aktif' if theme_park_mode else 'Nonaktif'}
• Random Seed: {seed_value}

1. POLA KEDATANGAN 5 PENGUNJUNG PERTAMA:
"""
        
        for arrival in sim.arrivals:
            result_text += f"   Pengunjung {arrival['customer']}: "
            result_text += f"Waktu antar = {arrival['inter_arrival']:.2f} menit, "
            result_text += f"Waktu kedatangan = {arrival['arrival_time']:.2f} menit"
            if sim.theme_park_mode:
                result_text += f", Wahana = {arrival['ride']}"
            result_text += "\n"
        
        result_text += "\n2. SIMULASI SISTEM:\n"
        for event in sim.events:
            result_text += f"   Event {event['sequence']}: {event['type']} Pengunjung {event['customer']} "
            result_text += f"pada waktu {event['time']:.2f} menit, "
            result_text += f"Dalam sistem = {event['in_system']}, "
            result_text += f"Antrian = {event['queue_length']}, "
            result_text += f"Status = {event['server_status']}\n"
        
        result_text += f"\n3. STATISTIK SISTEM:\n"
        result_text += f"   • Total waktu simulasi: {results['total_time']:.2f} menit\n"
        result_text += f"   • Tingkat kesibukan loket: {results['server_utilization']:.2%}\n"
        result_text += f"   • Rata-rata pengunjung dalam sistem: {results['avg_customers_in_system']:.2f}\n"
        result_text += f"   • Pengunjung dalam sistem (akhir): {results['final_customers_in_system']}\n"
        result_text += f"   • Panjang antrian (akhir): {results['final_queue_length']}\n"
        
        # Tombol download
        st.download_button(
            label="📥 Download Hasil Simulasi (TXT)",
            data=result_text,
            file_name=f"hasil_simulasi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
        
    else:
        # Tampilan awal
        st.markdown("""
        ## Selamat datang di Sistem Simulasi Antrian Tiket Wahana! 🎡
        
        Aplikasi ini mensimulasikan sistem antrian M/M/1 untuk pembelian tiket wahana di taman hiburan.
        
        ### Fitur:
        1. **Simulasi antrian** dengan distribusi eksponensial
        2. **Parameter yang dapat disesuaikan**:
           - Waktu antar kedatangan
           - Rata-rata waktu pelayanan
           - Jumlah event simulasi
        3. **Visualisasi hasil** dalam bentuk grafik
        4. **Perhitungan teoritis** sistem M/M/1
        5. **Download hasil** dalam format teks
        
        ### Cara Menggunakan:
        1. Atur parameter simulasi di sidebar
        2. Klik tombol **"Jalankan Simulasi"**
        3. Lihat hasil di panel utama
        4. Download hasil jika diperlukan
        
        ### Contoh Parameter Default:
        - Waktu antar kedatangan: [10, 12, 8, 15, 20] menit
        - Rata-rata waktu pelayanan: 15 menit
        - Jumlah event: 3
        """)
        
        # Tampilkan contoh visualisasi
        st.info("💡 Pilih parameter di sidebar dan klik 'Jalankan Simulasi' untuk memulai!")

if __name__ == "__main__":
    main()