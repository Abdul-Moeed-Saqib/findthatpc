import React from 'react';
import { Box, Text, Heading } from '@chakra-ui/react';

function ErrorPage() {
    return (
        <Box textAlign="center" py={10} px={6}>
            <Heading as="h1" size="2xl" mb={6} color="red.500">
                404 - Page Not Found
            </Heading>
            <Text fontSize="xl">
                Sorry, the page you are looking for does not exist.
            </Text>
        </Box>
    );
}

export default ErrorPage;