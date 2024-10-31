import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Heading } from "@chakra-ui/react";

function Header() {
    return (
        <Box
            as="header"
            bg="white"
            borderBottom="1px solid"
            borderColor="lightblue"
            p={4}
            width="100%"
        >
            <Heading as="h1" color="lightblue" size="lg" textAlign="left">
                <RouterLink RouterLink to="/">FindThatPC.AI</RouterLink>
            </Heading>
        </Box>
    );
}

export default Header;