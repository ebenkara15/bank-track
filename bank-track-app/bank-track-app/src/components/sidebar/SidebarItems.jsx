import { Box, Flex, Icon, Text, useColorModeValue } from "@chakra-ui/react"
import { FaArrowDownShortWide, FaDollarSign, FaScaleBalanced, FaWallet } from "react-icons/fa6"
import { Link } from "react-router-dom"




const items = [
    { icon: FaWallet, title: "Accounts", path: "/accounts" },
    { icon: FaScaleBalanced, title: "Balances", path: "/balances" },
    { icon: FaDollarSign, title: "Transactions", path: "/transactions" },
    { icon: FaArrowDownShortWide, title: "Categories", path: "/categories" },
]


const SidebarItems = () => {
    // const bgActive = useColorModeValue("#E2E8F0", "#E2E8F0")
    const textColor = useColorModeValue("navy", "#4A5568")

    const finalItems = [...items]

    const listItems = finalItems.map((item) => (
        <Flex
            as={Link}
            to={item.path}
            w="100%"
            p={2}
            key={item.title}
            activeprops={{
                style: {
                    background: "#E2E8F0",
                    borderRadius: "12px",
                },
            }}
            marginTop={2}
            color={textColor}
        >
            <Icon as={item.icon} alignSelf="center" />
            <Text ml={2}>{item.title}</Text>
        </Flex>
    ))

    return (
        <>
            <Box marginTop="10vh">{listItems}</Box >
        </>
    )
}

export default SidebarItems;
