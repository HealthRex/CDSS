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

        // Check if user prefers dark mode
        const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Customize the layout for better visualization
        graphData.layout.hovermode = 'closest';
        graphData.layout.xaxis.title = 'Time (Days in Treatment)';
        graphData.layout.yaxis.title = 'Retention Probability';
        graphData.layout.title = {
            text: 'Predicted Retention Probability Over Time',
            font: { 
                size: 18, 
                color: isDarkMode ? 'hsl(210 40% 98%)' : 'hsl(222.2 84% 4.9%)' 
            }
        };
        graphData.layout.margin = { l: 50, r: 50, t: 60, b: 120 };
        graphData.layout.font = { 
            family: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif', 
            size: 12, 
            color: isDarkMode ? 'hsl(210 40% 98%)' : 'hsl(222.2 84% 4.9%)' 
        };
        graphData.layout.paper_bgcolor = isDarkMode ? 'hsl(217.2 32.6% 17.5%)' : 'hsl(0 0% 100%)';
        graphData.layout.plot_bgcolor = isDarkMode ? 'hsl(217.2 32.6% 17.5%)' : 'hsl(0 0% 100%)';
        graphData.layout.showlegend = true;
        graphData.layout.legend = {
            orientation: 'h',
            yanchor: 'bottom',
            y: -0.4,
            xanchor: 'center',
            x: 0.5,
            font: {
                color: isDarkMode ? 'hsl(210 40% 98%)' : 'hsl(222.2 84% 4.9%)'
            }
        };
        
        // Update axis styling for dark mode
        if (isDarkMode) {
            graphData.layout.xaxis.tickcolor = 'hsl(217.2 32.6% 35%)';
            graphData.layout.xaxis.gridcolor = 'hsl(217.2 32.6% 25%)';
            graphData.layout.xaxis.linecolor = 'hsl(217.2 32.6% 35%)';
            graphData.layout.yaxis.tickcolor = 'hsl(217.2 32.6% 35%)';
            graphData.layout.yaxis.gridcolor = 'hsl(217.2 32.6% 25%)';
            graphData.layout.yaxis.linecolor = 'hsl(217.2 32.6% 35%)';
        }

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
    
    // Toggle the current panel (only show if it wasn't already visible)
    if (!isCurrentlyVisible) {
        infoElement.classList.add('show');
    }
}

// Function to update chart styling when theme changes
function updateChartTheme() {
    console.log('Theme change detected, updating chart...');
    const resultDiv = document.getElementById('result');
    
    if (!resultDiv) {
        console.log('Result div not found');
        return;
    }
    
    // Check if there's a Plotly chart
    if (resultDiv._fullLayout || (resultDiv.children.length > 0 && resultDiv.children[0]._fullLayout)) {
        const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        console.log('Dark mode:', isDarkMode);
        
        const updateLayout = {
            'title.font.color': isDarkMode ? 'hsl(210 40% 98%)' : 'hsl(222.2 84% 4.9%)',
            'font.color': isDarkMode ? 'hsl(210 40% 98%)' : 'hsl(222.2 84% 4.9%)',
            'plot_bgcolor': isDarkMode ? 'hsl(217.2 32.6% 17.5%)' : 'hsl(0 0% 100%)',
            'paper_bgcolor': isDarkMode ? 'hsl(217.2 32.6% 17.5%)' : 'hsl(0 0% 100%)',
            'legend.font.color': isDarkMode ? 'hsl(210 40% 98%)' : 'hsl(222.2 84% 4.9%)',
            'xaxis.tickcolor': isDarkMode ? 'hsl(217.2 32.6% 35%)' : '#333',
            'xaxis.gridcolor': isDarkMode ? 'hsl(217.2 32.6% 25%)' : '#eee',
            'xaxis.linecolor': isDarkMode ? 'hsl(217.2 32.6% 35%)' : '#333',
            'yaxis.tickcolor': isDarkMode ? 'hsl(217.2 32.6% 35%)' : '#333',
            'yaxis.gridcolor': isDarkMode ? 'hsl(217.2 32.6% 25%)' : '#eee',
            'yaxis.linecolor': isDarkMode ? 'hsl(217.2 32.6% 35%)' : '#333'
        };
        
        try {
            Plotly.relayout('result', updateLayout);
            console.log('Chart theme updated successfully');
        } catch (error) {
            console.error('Error updating chart theme:', error);
        }
    } else {
        console.log('No Plotly chart found');
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Set focus on the age input for better UX
    const ageInput = document.getElementById('age_at_drug_start');
    if (ageInput) {
        ageInput.focus();
    }
    
    // Listen for theme changes
    if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', updateChartTheme);
        console.log('Theme change listener registered');
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // Submit form with Ctrl/Cmd + Enter
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            event.preventDefault();
            document.getElementById("predictionForm").dispatchEvent(new Event('submit'));
        }
        
        // Close info panels with Escape
        if (event.key === 'Escape') {
            const visiblePanels = document.querySelectorAll('.info-panel.show');
            visiblePanels.forEach(panel => panel.classList.remove('show'));
        }
    });
});

