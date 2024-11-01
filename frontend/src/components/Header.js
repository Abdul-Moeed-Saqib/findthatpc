import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Heading, Text } from "@chakra-ui/react";

function Header() {
    return (
        <Box
            as="header"
            bg="white"
            borderBottom="1px solid"
            borderColor="lightblue"
            p={6} 
            width="100%"
            boxShadow="sm"
        >
            <Heading 
                as="h1" 
                color="blue.500" 
                size="2xl" 
                textAlign="left" 
                fontWeight="bold"
                letterSpacing="tight"
            >
                <RouterLink to="/">FindThatPC.AI</RouterLink>
            </Heading>
        </Box>
    );
}

export default Header;