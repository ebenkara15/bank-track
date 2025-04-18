import { Badge, Box, Button, Card, CardBody, CardHeader, Flex, Heading, Icon, Text } from "@chakra-ui/react";
import { FaPlus, FaRegCalendar } from "react-icons/fa6";

const AccountCard = ({ balances, product }) => {
    const positiveColor = "#4AB74E";
    const negativeColor = "#C5594D";
    const balance = balances[0];

    if (!balances) {
        return "No balances found";
    }
    else {
        return (
            <Card maxW='sm' key={balance.balance_id} margin={3}>
                <CardHeader
                    justify='space-between'
                    flexWrap='wrap'
                    alignItems='center'
                    as={Flex}
                >
                    <Box as={Flex} alignItems='center'>
                        <Heading size="md" color={balance.amount > 0 ? positiveColor : negativeColor} as={Box}>{balance.amount} {balance.currency}</Heading>
                        <Badge margin={2} color="#327AC0">{balance.balance_type}</Badge>
                    </Box>
                    <Text color="gray.500" as={Box}><Icon as={FaRegCalendar} /> {balance.reference_date}</Text>
                </CardHeader>

                <CardBody>
                    <Button variant='ghost' size='sm'><Icon as={FaPlus} /> Add category</Button>
                    <Box as={Flex} justifyContent='start' flexWrap="wrap">
                        <Badge margin={2} color="#327AC0">{balance.balance_type}</Badge>
                    </Box>
                </CardBody>
            </Card>
        );
    }
};

export default AccountCard
