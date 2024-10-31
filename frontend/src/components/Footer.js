import React from 'react';
import { Box, Text } from "@chakra-ui/react";

function Footer() {
    return (
        <Box
            as="footer"
            position="fixed"
            bottom="0"
            width="100%"
            bg="white"
            borderTop="1px solid"
            borderColor="lightblue"
            p={4}
            textAlign="center"
        >
            <Text color="lightblue">© 2024 FindThatPC.AI. All rights reserved.</Text>
        </Box>
    );
}

export default Footer;