import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Header from './components/Header';
import Dashboard from './components/Dashboard';
import ManualPredict from './components/ManualPredict';
import Search from './components/Search';
import History from './components/History';
import Analytics from './components/Analytics';
import DatabaseService from './services/DatabaseService';

function App() {
  const [currentModel, setCurrentModel] = useState('pretrained');
  const [results, setResults] = useState([]);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const data = await DatabaseService.loadAllData();
        setResults(data.predictions || []);
      } catch (error) {
        console.error('Error loading initial data:', error);
      }
    };

    loadInitialData();
  }, []);

  const handleNewResult = async (res) => {
    setResults(prev => [...prev, res]);

    try {
      await DatabaseService.savePrediction(res);
    } catch (error) {
      console.error('Error saving prediction:', error);
    }
  };

  return (
    <Router>
      <div style={{ background: '#0c0c0c', minHeight: '100vh' }}>
        <Header
          currentModel={currentModel}
          onModelSwitch={setCurrentModel}
        />

        <div style={{ paddingTop: '80px' }}>
          <Routes>
            <Route
              path="/"
              element={
                <Dashboard
                  currentModel={currentModel}
                  results={results}
                />
              }
            />

            <Route
              path="/predict-manual"
              element={
                <ManualPredict onSearchResult={handleNewResult} />
              }
            />

            <Route
              path="/search"
              element={
                <Search onSearchResult={handleNewResult} />
              }
            />

            <Route
              path="/history"
              element={
                <History searchResults={results} />
              }
            />

            <Route
              path="/analytics"
              element={
                <Analytics
                  searchResults={results}
                  currentModel={currentModel}
                />
              }
            />
          </Routes>
        </div>

        <ToastContainer
          position="top-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme="dark"
        />
      </div>
    </Router>
  );
}

export default App;