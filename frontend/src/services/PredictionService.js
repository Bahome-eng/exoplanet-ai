class PredictionService {
  constructor() {
    this.currentDataset = null;
    this.currentCandidate = null;
    this.baseURL = 'http://127.0.0.1:5000';
  }

  setSelection(dataset, candidateId) {
    this.currentDataset = dataset;
    this.currentCandidate = candidateId;
    console.log(`Selected: ${dataset} - ${candidateId}`);
  }

  async getCandidates() {
    try {
      const response = await fetch(`${this.baseURL}/api/autocomplete/kepler`);
      if (response.ok) {
        const data = await response.json();
        return data.suggestions || [];
      } else {
        throw new Error('Failed to load Kepler candidates');
      }
    } catch (error) {
      console.error('Error getting candidates:', error);
      return [];
    }
  }

  async searchCandidates(dataset, query) {
    try {
      const allCandidates = await this.getCandidates(dataset);
      if (query) {
        return allCandidates.filter(candidate =>
          candidate.toLowerCase().includes(query.toLowerCase())
        );
      }
      return allCandidates;
    } catch (error) {
      console.error('Error searching candidates:', error);
      return [];
    }
  }

  async makePrediction() {
    if (!this.currentCandidate) {
      throw new Error('No candidate selected');
    }

    try {
      const response = await fetch(`${this.baseURL}/api/predict/kepler`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          koi_name: this.currentCandidate
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Prediction failed');
      }

      const data = await response.json();

      if (data.prediction) {
        return {
          status: 'success',
          dataset: this.currentDataset,
          candidate_id: this.currentCandidate,
          confidence: Math.round(data.prediction.confidence * 100) / 100,
          is_exoplanet: data.prediction.is_exoplanet,
          model_version: data.prediction.model_version,
          nasa_classification: data.nasa_classification || 'UNKNOWN',
          message: data.message || `Prediction completed for ${this.currentCandidate}`
        };
      } else {
        throw new Error('Invalid response from prediction API');
      }
    } catch (error) {
      return {
        status: 'error',
        message: `Prediction failed: ${error.message}`
      };
    }
  }

  getCurrentSelection() {
    return {
      dataset: this.currentDataset,
      candidate: this.currentCandidate
    };
  }

  async generateLightcurve() {
    if (!this.currentCandidate) {
      throw new Error('No candidate selected');
    }

    try {
      const response = await fetch(`${this.baseURL}/api/lightcurve/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          koi_name: this.currentCandidate
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Lightcurve generation failed');
      }

      const data = await response.json();

      if (data.success) {
        return {
          status: 'success',
          filename: data.filename,
          title: data.title,
          url: `${this.baseURL}${data.url}`
        };
      } else {
        throw new Error(data.error || 'Lightcurve generation failed');
      }
    } catch (error) {
      return {
        status: 'error',
        message: `Lightcurve generation failed: ${error.message}`
      };
    }
  }

  clearSelection() {
    this.currentDataset = null;
    this.currentCandidate = null;
  }
}

const predictionService = new PredictionService();
export default predictionService;