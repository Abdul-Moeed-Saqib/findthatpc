import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Box, Button, Input, Spinner, VStack, Text, HStack, Link as ChakraLink, Grid, ScaleFade, Fade, useToast
} from '@chakra-ui/react';

const Comparison = () => {
    const toast = useToast();
    const [url, setURL] = useState('');
    const [loading, setLoading] = useState(false);
    const [comparisonData, setComparisonData] = useState(null);
    const [visibleParts, setVisibleParts] = useState([]);
    const [allComponentsDisplayed, setAllComponentsDisplayed] = useState(false);

    const handleStartComparison = async () => {
        setLoading(true);
        setComparisonData(null);
        setVisibleParts([]);
        setAllComponentsDisplayed(false);
        try {
            const response = await axios.post('/scrape', { url: url.trim() });
            setComparisonData(response.data);
        } catch (error) {
            console.error("Error fetching data:", error);
            toast({
                title: "Error",
                description: error.response?.data?.error || "An unexpected error occurred.",
                status: "error",
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (comparisonData) {
            const displayComponents = async () => {
                comparisonData.parts.forEach((_, index) => {
                    setTimeout(() => {
                        setVisibleParts(prev => [...prev, index]);
                        if (index === comparisonData.parts.length - 1) {
                            setAllComponentsDisplayed(true);
                        }
                    }, index * 200);
                });
            };
            displayComponents();
            setURL("");
        }
    }, [comparisonData]);

    return (
        <VStack spacing={6} mt={10} align="stretch" maxWidth="1200px" mx="auto">
            {!comparisonData && (
                <>
                    <Box textAlign="center" maxWidth="600px" mx="auto" mb={4}>
                        <Text fontSize="lg" fontWeight="medium">
                            Welcome to FindThatPC.AI! This tool allows you to compare the price of a prebuilt PC with the cost of building it yourself.
                            Simply enter a link to a prebuilt PC from Newegg or Canada Computers, and we’ll break down the prices for each individual component.
                            Our app helps you decide if buying a prebuilt is worth it or if building from parts is a more budget-friendly option.
                        </Text>
                        <Text fontSize="lg" mt={2}>
                            Note: Please use only product links from Newegg or Canada Computers. Example URLs:
                        </Text>
                        <Text fontSize="sm" color="gray.500" mt={1}>
                            - https://www.newegg.com/productpage
                        </Text>
                        <Text fontSize="sm" color="gray.500">
                            - https://www.canadacomputers.com/productpage
                        </Text>
                    </Box>

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
                        isDisabled={!url.trim() || loading}
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
                <HStack align="start" spacing={8} mt={10} w="100%" alignItems="flex-start">
                    <VStack
                        align="start"
                        spacing={5}
                        w="30%"
                        position="absolute"
                        top="130px"
                        left="20px"
                    >
                        <Fade in={!!comparisonData}>
                            <Box p={6} mt={5} shadow="md" borderWidth="2px" borderRadius="lg" bg="blue.50" w="110%">
                                <Text fontSize="xx-large" fontWeight="bold" color="blue.600">Prebuilt PC Information</Text>
                                <Text mt={4} fontSize="x-large"><strong>Name:</strong> {comparisonData.prebuilt_name}</Text>
                                <Text fontSize="x-large"><strong>Price:</strong> ${comparisonData.prebuilt_price.toFixed(2)}</Text>
                             </Box>
                            <Box p={6} mt={5} shadow="md" borderWidth="2px" borderRadius="lg" bg="green.50" w="110%">
                                <Text fontSize="xx-large" fontWeight="bold" color="green.600">Price Difference</Text>
                                <Text mt={4} fontSize="x-large"><strong>Total Parts Price:</strong> ${comparisonData.total_parts_price.toFixed(2)}</Text>
                                <Text fontSize="x-large"><strong>Difference:</strong> ${comparisonData.price_difference.toFixed(2)}</Text>
                            </Box>
                        </Fade>
                        {allComponentsDisplayed && (
                        <Fade in={allComponentsDisplayed}>
                            <Box p={10} mt={150} textAlign="center">
                                <Text fontSize="x-large" fontWeight="bold" color="purple.600">
                                    Want to try another prebuilt PC?
                                </Text>
                                <Button mt={4} colorScheme="purple" onClick={() => setComparisonData(null)}>
                                    Compare Another PC
                                </Button>
                            </Box>
                        </Fade>
                    )}
                    </VStack>
                    
                    <Box w="100%" pl="350px">
                        <Box w="135%" textAlign="center" mb={6}>
                            <Text fontSize="xx-large" fontWeight="bold" color="gray.700" textAlign="center">
                                Components
                            </Text>
                        </Box>
                        <Grid templateColumns="repeat(3, 1fr)" gap={10}>
                            {comparisonData.parts.map((part, index) => (
                                <ScaleFade in={visibleParts.includes(index)} initialScale={0.9} key={index}>
                                    <Box 
                                        p={6} 
                                        shadow="lg" 
                                        borderWidth="2px" 
                                        borderRadius="lg" 
                                        bg="white" 
                                        h="250px" 
                                        w="300px" 
                                        display="flex" 
                                        flexDirection="column" 
                                        justifyContent="space-between"
                                    >
                                        <Box>
                                            <Text fontSize="xl" fontWeight="semibold" color="teal.600">{part.name}</Text>
                                            <Text><strong>Type:</strong> {part.type}</Text>
                                            <Text><strong>Price:</strong> ${part.price.toFixed(2)}</Text>
                                        </Box>
                                        <Box display="flex" justifyContent="center" mt={4}>
                                            <Button as={ChakraLink} href={part.link} target="_blank" colorScheme="blue">
                                                View Part
                                            </Button>
                                        </Box>
                                    </Box>
                                </ScaleFade>
                            ))}
                        </Grid>
                    </Box>
                </HStack>
            )}
        </VStack>
    );
};

export default Comparison;