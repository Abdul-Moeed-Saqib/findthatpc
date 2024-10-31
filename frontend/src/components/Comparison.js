import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Box, Button, Input, Spinner, VStack, Text, HStack, Link as ChakraLink, Grid,
} from '@chakra-ui/react';

const Comparison = () => {
    const [url, setURL] = useState('');
    const [loading, setLoading] = useState(false);
    const [comparisonData, setComparisonData] = useState(null);

    const handleStartComparison = async () => {
        setLoading(true);
        try {
            const response = await axios.post('/scrape', { url: url.trim() });
            setComparisonData(response.data);
        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <VStack spacing={6} mt={10} align="stretch">
            {!comparisonData && (
                <>
                    <Input
                        placeholder="Enter prebuilt PC link"
                        value={url}
                        onChange={(e) => setURL(e.target.value)}
                        size="lg"
                        maxWidth="500px" 
                        mx="auto" 
                    />
                    <Button
                        colorScheme="blue"
                        onClick={handleStartComparison}
                        isDisabled={!url.trim() || loading === true}
                        maxWidth="200px" 
                        mx="auto" 
                    >
                        Start Comparison
                    </Button>
                </>
            )}

            {loading && (
                <Box display="flex" justifyContent="center" alignItems="center" height="200px">
                    <Spinner size="lg" color="teal.500" label="Please wait, generating the result..." />
                </Box>
            )}

            {comparisonData && (
                <HStack align="start" spacing={10} mt={10} w="100%">
                    <VStack align="start" w="30%" spacing={5}>
                        <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg="gray.50">
                            <Text fontSize="xl" fontWeight="bold">Prebuilt PC Information</Text>
                            <Text mt={2}><strong>Name:</strong> {comparisonData.prebuilt_name}</Text>
                            <Text><strong>Price:</strong> ${comparisonData.prebuilt_price.toFixed(2)}</Text>
                        </Box>
                        <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg="gray.50">
                            <Text fontSize="xl" fontWeight="bold">Price Difference</Text>
                            <Text mt={2}><strong>Total Parts Price:</strong> ${comparisonData.total_parts_price.toFixed(2)}</Text>
                            <Text><strong>Difference:</strong> ${comparisonData.price_difference.toFixed(2)}</Text>
                        </Box>
                    </VStack>

                    <Box w="70%">
                        <Text fontSize="xl" fontWeight="bold" mb={4}>Components</Text>
                        <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={4}>
                            {comparisonData.parts.map((part, index) => (
                                <Box key={index} p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg="white">
                                    <Text fontSize="lg" fontWeight="bold">{part.name}</Text>
                                    <Text><strong>Type:</strong> {part.type}</Text>
                                    <Text><strong>Price:</strong> ${part.price.toFixed(2)}</Text>
                                    <Button as={ChakraLink} href={part.link} target="_blank" colorScheme="blue" mt={3}>
                                        View Part
                                    </Button>
                                </Box>
                            ))}
                        </Grid>
                    </Box>
                </HStack>
            )}
        </VStack>
    );
};

export default Comparison;