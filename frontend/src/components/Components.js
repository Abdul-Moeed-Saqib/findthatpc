import React from 'react';
import { Box, Text, Grid, ScaleFade, Button, Link as ChakraLink } from '@chakra-ui/react';

const Components = ({ parts, visibleParts, currencySymbol}) => {
    return (
        <Box w="100%" pl="350px">
            <Box w="135%" textAlign="center" mb={6}>
                <Text fontSize="xx-large" fontWeight="bold" color="gray.700" textAlign="center">
                    Components
                </Text>
            </Box>
            <Grid templateColumns="repeat(3, 1fr)" gap={10}>
                {parts.map((part, index) => (
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
                                <Text><strong>Price:</strong> {currencySymbol}{part.price.toFixed(2)}</Text>
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
    );
};

export default Components;