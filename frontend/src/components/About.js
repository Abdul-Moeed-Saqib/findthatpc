import React from 'react';
import {
  Box,
  Heading,
  Text,
  VStack,
  Divider,
  Image,
} from '@chakra-ui/react';

function About() {
  return (
    <VStack spacing={8} align="start" width="100%" py={8} px={4}>
      <Box w="100%">
      <Image
          src="/SQCorp.png"
          alt="About FindThatPC.AI"
          rounded="md"
          shadow="md"
          objectFit="contain"
          w="100%"
          maxW="300px"
          mx="auto"
        />
        <Text
          fontSize="sm"
          color="gray.500"
          textAlign="center"
          mt={2}
        >
          Created by SQ Corp
        </Text>
      </Box>

      <Box w="100%">
        <Heading size="xl" color="blue.500" mb={4}>
          About FindThatPC.AI
        </Heading>
        <Text fontSize="lg" color="gray.700">
          FindThatPC.AI is your smart assistant for comparing prebuilt PCs
          against custom parts lists. We help you find out if you're getting
          the best value for your money — fast, simple, and accurate.
        </Text>
      </Box>

      <Divider />

      <Box w="100%">
        <Heading size="lg" color="blue.400" mb={2}>
          What It Does
        </Heading>
        <Text fontSize="md" color="gray.600">
          My platform analyzes prebuilt PCs from top retailers and breaks them
          down into their individual components — CPUs, GPUs, storage, memory,
          cooling, and more. Then fetch the current best prices for each part,
          so you can see if the prebuilt PC is fairly priced or if building
          your own would save you hundreds of dollars.
        </Text>
      </Box>

      <Divider />

      <Box w="100%">
        <Heading size="lg" color="blue.400" mb={2}>
          How It Works
        </Heading>
        <VStack align="start" spacing={4} pl={4}>
          <Text fontSize="md" color="gray.600">
            1. Paste a link to a prebuilt PC from supported retailers (like
            Microcenter or CanadaComputers).
          </Text>
          <Text fontSize="md" color="gray.600">
            2. Our AI breaks down the build, finds the individual parts, and
            fetches their prices.
          </Text>
          <Text fontSize="md" color="gray.600">
            3. Instantly compare the total cost of building it yourself versus
            buying the prebuilt — side by side.
          </Text>
        </VStack>
      </Box>

      <Divider />

      <Box w="100%">
        <Heading size="lg" color="blue.400" mb={2}>
          Why I Built This
        </Heading>
        <Text fontSize="md" color="gray.600">
          FindThatPC.AI was created by passionate PC enthusiasts who believe
          that smart buying decisions shouldn't require hours of research. With
          the rising costs of hardware, it's more important than ever to
          understand what you're paying for. My mission is to empower users
          with transparent, easy-to-understand information so that you can make
          the best choice — whether you're buying a gaming rig, a workstation,
          or your next upgrade.
        </Text>
      </Box>
    </VStack>
  );
}

export default About;