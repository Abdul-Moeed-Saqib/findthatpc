import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Button, Text, VStack } from '@chakra-ui/react';

const Home = () => {
    const navigate = useNavigate();

    return (
        <VStack spacing={6} mt={10} textAlign="center">
            <Box>
                <Text fontSize="xxx-large" fontWeight="bold">Welcome to FindThatPC.AI</Text>
                <Text fontSize="lg" mt={4}>
                    FindThatPC.AI compares the prices of prebuilt PCs against individual components.
                </Text>
                <Text fontSize="md" mt={4}>
                    We support only <strong>Newegg</strong> and <strong>CanadaComputers</strong> links.
                </Text>
            </Box>
            <Button colorScheme="blue" onClick={() => navigate('/comparison')}>
                Continue
            </Button>
        </VStack>
    );
};

export default Home;