# dashboard/views.py
from django.shortcuts import render
import pandas as pd
from .analyze import analyze, plot

def dashboard_view(request):
    results = None
    plot_day = None
    plot_hour = None

    if request.method == 'POST' and request.FILES.get('spotify_file'):
        uploaded_file = request.FILES['spotify_file']

        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df = pd.read_json(uploaded_file)
            else:
                results = "Unsupported file type. Please upload JSON or CSV."
                return render(request, 'dashboard/dashboard.html', {
                    'plot_day': None,
                    'plot_hour': None,
                    'results': results
                })

            # Analyze and get plots
            enriched_df, results = analyze(df)
            plot_day, plot_hour = plot(enriched_df)

        except Exception as e:
            results = f"An error occurred: {e}"
            plot_day = None
            plot_hour = None

    return render(request, 'dashboard/dashboard.html', {
        'plot_day': plot_day,
        'plot_hour': plot_hour,
        'results': results
    })
