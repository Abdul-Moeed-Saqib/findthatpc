import React from 'react';
import { NavLink } from 'react-router-dom';
import { Box, Heading, Image, HStack, Link as ChakraLink } from "@chakra-ui/react";

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
        fontWeight="bold"
        letterSpacing="tight"
      >
        <NavLink to="/">FindThatPC.AI</NavLink>
      </Heading>

      <HStack spacing={5} ml="auto">
        {[
          { label: 'Home', to: '/' },
          { label: 'About', to: '/about' },
        ].map(({ label, to }) => (
          <ChakraLink
            key={to}
            as={NavLink}
            to={to}
            fontSize="lg"
            fontWeight="semibold"
            px={3}
            py={2}
            rounded="md"
            _hover={{ bg: 'blue.50', color: 'blue.600', textDecoration: 'none' }}
            _activeLink={{ bg: 'blue.100', color: 'blue.700' }}
          >
            {label}
          </ChakraLink>
        ))}
      </HStack>
    </Box>
  );
}

export default Header;