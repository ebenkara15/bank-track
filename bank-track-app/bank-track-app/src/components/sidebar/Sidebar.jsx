import {
    Box,
    Flex,
    Heading,
    useColorModeValue
} from "@chakra-ui/react"

import SidebarItems from "./SidebarItems"

const Sidebar = () => {
    const bgColor = useColorModeValue("#FFFFFF", "ui.dark")
    // const textColor = useColorModeValue("ui.dark", "ui.white")
    const secBgColor = useColorModeValue("ui.secondary", "ui.darkSlate")


    return (
        <>
            {/* Desktop */}
            <Box
                bg={bgColor}
                p={3}
                h="100vh"
                position="sticky"
                top="0"
                w={{ base: "33vw", md: "25vw" }}
                maxW={{ base: "33vw", md: "25vw" }}
                display={{ base: "none", md: "flex" }}
                borderRight={"solid"}
                borderRightColor={"gray.100"}
            >
                <Flex
                    flexDir="column"
                    justify="space-between"
                    bg={secBgColor}
                    p={4}
                    borderRadius={12}
                >
                    <Box>
                        {/* <Image src={Logo} alt="Logo" w="180px" maxW="2xs" p={6} /> */}
                        <Heading color="navy" size="lg">Bank Track</Heading>
                        <SidebarItems />
                    </Box>

                </Flex>
            </Box>
        </>
    )
}

export default Sidebar
