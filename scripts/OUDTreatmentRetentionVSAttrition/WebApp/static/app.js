// Auto-update functionality
let autoUpdateEnabled = true;
let updateTimeout = null;

// Debounce function to prevent too frequent updates
function debounce(func, wait) {
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(updateTimeout);
            func(...args);
        };
        clearTimeout(updateTimeout);
        updateTimeout = setTimeout(later, wait);
    };
}

// Function to collect form data
function getFormData() {
    const form = document.getElementById("predictionForm");
    const formData = new FormData(form);
    
    return {
        "438120": formData.get("opioid_dependence") ? 1 : 0,
        "938268": formData.get("limb_swelling") ? 1 : 0,
        "986417": formData.get("laxative") ? 1 : 0,
        "1124957": formData.get("oxycodone") ? 1 : 0,
        "1125315": formData.get("acetaminophen") ? 1 : 0,
        "chronic_pain": formData.get("chronic_pain") ? 1 : 0,
        "liver_disease": formData.get("liver_disease") ? 1 : 0,
        "age_at_drug_start": parseFloat(formData.get("age_at_drug_start")) || 0,
        "4145308": formData.get("ecg") ? 1 : 0,
        "1129625": formData.get("diphenhydramine") ? 1 : 0,
        "941258": formData.get("docusate") ? 1 : 0,
        "4336384": formData.get("opioid_withdrawal") ? 1 : 0,
        "1112807": formData.get("aspirin") ? 1 : 0,
        "major_depression": formData.get("major_depression") ? 1 : 0,
        "1133201": formData.get("buprenorphine") ? 1 : 0
    };
}

// Function to make prediction
async function makePrediction(features, showLoading = true) {
    // Convert the features object to an array, ensuring the correct order
    const featuresArray = [
        features["438120"],
        features["938268"],
        features["986417"],
        features["1124957"],
        features["1125315"],
        features["chronic_pain"],
        features["liver_disease"],
        features["age_at_drug_start"],
        features["4145308"],
        features["1129625"],
        features["941258"],
        features["4336384"],
        features["1112807"],
        features["major_depression"],
        features["1133201"]
    ];

    // Check if we have required age field
    if (!features["age_at_drug_start"] || features["age_at_drug_start"] < 16 || features["age_at_drug_start"] > 95) {
        document.getElementById("result").innerHTML = `
            <div class="text-center text-muted-foreground">
                <i class="fas fa-exclamation-triangle text-4xl mb-4 opacity-50"></i>
                <p>Please enter a valid age between 16-95 years to generate predictions.</p>
            </div>
        `;
        return;
    }

    const submitButton = document.querySelector('.submit-button');
    const resultDiv = document.getElementById("result");

    if (showLoading) {
        // Show loading state
        submitButton.classList.add('loading');
        submitButton.innerHTML = '<i class="fas fa-spinner mr-2"></i>Generating...';
        
        resultDiv.innerHTML = `
            <div class="text-center text-muted-foreground">
                <i class="fas fa-spinner fa-spin text-4xl mb-4 opacity-50"></i>
                <p>Generating retention probability prediction...</p>
            </div>
        `;
    }

    try {
        // Send the data to the backend API
        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ features: featuresArray })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Handle the response
        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }

        // Parse the graphJSON from the response
        const graphData = JSON.parse(result.graphJSON);

        // Apply brand styling without changing any chart data.
        const chartStyles = {
            "Patient Prediction": { color: "#2ABEC0", width: 3, dash: "solid" },
            "Median": { color: "#0D2551", width: 2, dash: "dash" },
            "High Risk": { color: "#5B55C4", width: 2, dash: "dot" },
            "Low Risk": { color: "#8FA3BF", width: 2, dash: "dot" }
        };

        graphData.data.forEach((trace) => {
            const traceStyle = chartStyles[trace.name];
            if (!traceStyle) {
                return;
            }

            trace.line = {
                ...(trace.line || {}),
                color: traceStyle.color,
                width: traceStyle.width,
                dash: traceStyle.dash
            };

            if (trace.marker) {
                trace.marker = {
                    ...trace.marker,
                    color: traceStyle.color
                };
            }
        });

        // Customize chart presentation only; axes and prediction data are unchanged.
        graphData.layout.hovermode = 'closest';
        graphData.layout.title = {
            text: 'Predicted Retention Probability Over Time',
            x: 0.02,
            xanchor: 'left',
            font: {
                family: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                size: 18,
                color: '#0D2347'
            }
        };
        graphData.layout.margin = { l: 64, r: 24, t: 68, b: 108 };
        graphData.layout.font = {
            family: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            size: 12,
            color: '#5B6B85'
        };
        graphData.layout.paper_bgcolor = '#FFFFFF';
        graphData.layout.plot_bgcolor = '#FFFFFF';
        graphData.layout.showlegend = true;
        graphData.layout.legend = {
            orientation: 'h',
            yanchor: 'top',
            y: -0.24,
            xanchor: 'center',
            x: 0.5,
            font: {
                family: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                size: 11,
                color: '#5B6B85'
            }
        };

        graphData.layout.xaxis = {
            ...graphData.layout.xaxis,
            title: {
                text: 'Time (Days in Treatment)',
                font: { color: '#5B6B85', size: 12 }
            },
            gridcolor: '#E3E8F0',
            linecolor: '#E3E8F0',
            tickcolor: '#E3E8F0',
            tickfont: { color: '#5B6B85' },
            zeroline: false
        };
        graphData.layout.yaxis = {
            ...graphData.layout.yaxis,
            title: {
                text: 'Retention Probability',
                font: { color: '#5B6B85', size: 12 }
            },
            gridcolor: '#E3E8F0',
            linecolor: '#E3E8F0',
            tickcolor: '#E3E8F0',
            tickfont: { color: '#5B6B85' },
            zeroline: false
        };

        // Clear the result div completely before rendering
        resultDiv.innerHTML = '';
        
        // Render the plot using Plotly
        Plotly.newPlot('result', graphData.data, graphData.layout, {
            responsive: true, 
            displayModeBar: false,
            autosize: true
        });
        

    } catch (error) {
        console.error("Error:", error);
        resultDiv.innerHTML = `
            <div class="text-center text-red-600">
                <i class="fas fa-exclamation-circle text-4xl mb-4 opacity-50"></i>
                <p class="font-medium">Error: Could not generate prediction</p>
                <p class="text-sm opacity-75">${error.message}</p>
            </div>
        `;
    } finally {
        // Always reset button state if it's in loading mode
        if (submitButton.classList.contains('loading')) {
            submitButton.classList.remove('loading');
            submitButton.innerHTML = '<i class="fas fa-chart-line mr-2"></i>Generate Prediction';
        }
    }
}

// Debounced auto-update function
const debouncedAutoUpdate = debounce(async () => {
    if (autoUpdateEnabled) {
        const features = getFormData();
        await makePrediction(features, false);
    }
}, 1000);

// Function to handle button state and trigger auto-update
function triggerAutoUpdate() {
    if (autoUpdateEnabled) {
        const submitButton = document.querySelector('.submit-button');
        submitButton.classList.add('loading');
        submitButton.innerHTML = '<i class="fas fa-spinner mr-2"></i>Updating...';
        debouncedAutoUpdate();
    }
}

// Form submission handler
document.getElementById("predictionForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    const features = getFormData();
    await makePrediction(features, true);
});

// Auto-update on form changes
document.getElementById("predictionForm").addEventListener("input", function() {
    triggerAutoUpdate();
});

// Auto-update on checkbox changes
document.getElementById("predictionForm").addEventListener("change", function(event) {
    if (event.target.type === "checkbox") {
        triggerAutoUpdate();
    }
});

// Function to toggle the display of information panels with modern styling
function toggleInfo(infoId) {
    const infoElement = document.getElementById(infoId);
    const isCurrentlyVisible = infoElement.classList.contains('show');
    
    // Close all other info panels first
    const allInfoPanels = document.querySelectorAll('.info-panel');
    allInfoPanels.forEach(panel => {
        panel.classList.remove('show');
    });
    document.querySelectorAll('.info-button').forEach(button => {
        button.setAttribute('aria-expanded', 'false');
    });
    
    // Toggle the current panel (only show if it wasn't already visible)
    if (!isCurrentlyVisible) {
        infoElement.classList.add('show');
        const controllingButton = Array.from(document.querySelectorAll('.info-button')).find(button =>
            button.getAttribute('aria-controls') === infoId
        );
        if (controllingButton) {
            controllingButton.setAttribute('aria-expanded', 'true');
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Set focus on the age input for better UX
    const ageInput = document.getElementById('age_at_drug_start');
    if (ageInput) {
        ageInput.focus();
    }

    // Keep the existing help controls keyboard-accessible without toggling
    // a checkbox when its nested information button is activated.
    document.querySelectorAll('.info-button').forEach(button => {
        const handler = button.getAttribute('onclick') || '';
        const match = handler.match(/toggleInfo\('([^']+)'\)/);
        if (match) {
            button.setAttribute('aria-controls', match[1]);
            button.setAttribute('aria-expanded', 'false');
        }
        button.addEventListener('click', event => {
            event.preventDefault();
            event.stopPropagation();
        });
    });
});
