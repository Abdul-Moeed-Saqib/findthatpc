import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, Box } from '@chakra-ui/react';
import Home from './components/Home';
import Comparison from './components/Comparison';
import Header from './components/Header';
import Footer from './components/Footer';

function App() {
    return (
        <Router>
            <Header />
            <Container maxW="container.lg" centerContent flex={1} py={6} pb="100px">
                <Box w="100%">
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/comparison" element={<Comparison />} />
                    </Routes>
                </Box>
            </Container>
            <Footer />
        </Router>
    );
}

export default App;