class DatabaseService {
    constructor() {
      this.baseURL = 'http://127.0.0.1:5000';
    }
  
    async savePrediction(predictionData) {
      try {
        const response = await fetch(`${this.baseURL}/api/predictions/save`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(predictionData),
        });
  
        if (response.ok) {
          console.log('Prediction saved to database');
          return true;
        } else {
          console.error('Failed to save prediction:', await response.text());
          return false;
        }
      } catch (error) {
        console.error('Error saving prediction:', error);
        return false;
      }
    }
  
    async loadPredictions() {
      try {
        const response = await fetch(`${this.baseURL}/api/predictions`);
  
        if (response.ok) {
          const data = await response.json();
          console.log(`Loaded ${data.count} predictions from database`);
          return data.predictions || [];
        } else {
          console.error('Failed to load predictions:', await response.text());
          return [];
        }
      } catch (error) {
        console.error('Error loading predictions:', error);
        return [];
      }
    }
  
    async loadStats() {
      try {
        const response = await fetch(`${this.baseURL}/api/predictions/stats`);
  
        if (response.ok) {
          const stats = await response.json();
          console.log('Loaded stats from database:', stats);
          return stats;
        } else {
          console.error('Failed to load stats:', await response.text());
          return {
            total_predictions: 0,
            exoplanets_found: 0,
            average_confidence: 0,
            dataset_breakdown: {},
            success_rate: 0,
          };
        }
      } catch (error) {
        console.error('Error loading stats:', error);
        return {
          total_predictions: 0,
          exoplanets_found: 0,
          average_confidence: 0,
          dataset_breakdown: {},
          success_rate: 0,
        };
      }
    }
  
    async loadAllData() {
      try {
        const [predictions, stats] = await Promise.all([
          this.loadPredictions(),
          this.loadStats(),
        ]);
  
        return {
          predictions,
          stats,
        };
      } catch (error) {
        console.error('Error loading all data:', error);
        return {
          predictions: [],
          stats: {
            total_predictions: 0,
            exoplanets_found: 0,
            average_confidence: 0,
            dataset_breakdown: {},
            success_rate: 0,
          },
        };
      }
    }
  }
  
  const databaseService = new DatabaseService();
  export default databaseService;