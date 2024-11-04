import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Heading, Image } from "@chakra-ui/react";

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
            display="flex"
            alignItems="center"
        >
            <Image 
                src={`/chip.png`} 
                alt="Logo" 
                boxSize="50px" 
                mr={4}
            />
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