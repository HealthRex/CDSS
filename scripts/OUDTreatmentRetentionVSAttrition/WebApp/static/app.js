document.getElementById("predictionForm").addEventListener("submit", async function(event) {
    event.preventDefault();  // Prevent the form from submitting the traditional way

    // Get form data
    const formData = new FormData(event.target);

    // Convert form data to a JSON object, ensuring the correct order of features
    const features = {
        "438120": formData.get("opioid_dependence") ? 1 : 0,
        "938268": formData.get("limb_swelling") ? 1 : 0,
        "986417": formData.get("laxative") ? 1 : 0,
        "1124957": formData.get("oxycodone") ? 1 : 0,
        "1125315": formData.get("acetaminophen") ? 1 : 0,
        "chronic_pain": formData.get("chronic_pain") ? 1 : 0,
        "liver_disease": formData.get("liver_disease") ? 1 : 0,
        "age_at_drug_start": parseFloat(formData.get("age_at_drug_start")),
        "4145308": formData.get("ecg") ? 1 : 0,
        "1129625": formData.get("diphenhydramine") ? 1 : 0,
        "941258": formData.get("docusate") ? 1 : 0,
        "4336384": formData.get("opioid_withdrawal") ? 1 : 0,
        "1112807": formData.get("aspirin") ? 1 : 0,
        "major_depression": formData.get("major_depression") ? 1 : 0,
        "1133201": formData.get("buprenorphine") ? 1 : 0
    };

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

    try {
        // Send the data to the backend API
        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ features: featuresArray })
        });

        // Handle the response
        const result = await response.json();
        console.log(result);

        // Parse the graphJSON from the response
        const graphData = JSON.parse(result.graphJSON);
        console.log(graphData);

        // Customize the layout for better visualization
        graphData.layout.hovermode = 'closest'; // Enable hovermode for better interactivity
        graphData.layout.xaxis.title = 'Time (Days in Treatment)'; // Customize x-axis title
        graphData.layout.yaxis.title = 'Retention Probability'; // Customize y-axis title
        graphData.layout.title = 'Predicted Retention Probability Over Time'; // Add a title to the graph
        graphData.layout.margin = { l: 60, r: 40, t: 60, b: 40 }; // Adjust margins
        graphData.layout.font = { family: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', size: 14, color: '#333' };

        // Render the plot using Plotly
        Plotly.newPlot('result', graphData.data, graphData.layout);

    } catch (error) {
        console.error("Error:", error);
        document.getElementById("result").textContent = "Error: Could not get prediction.";
    }
});

// Function to toggle the display of information text
function toggleInfo(infoId) {
    const infoElement = document.getElementById(infoId);
    if (infoElement.style.display === "none" || infoElement.style.display === "") {
        infoElement.style.display = "block";
    } else {
        infoElement.style.display = "none";
    }
}
