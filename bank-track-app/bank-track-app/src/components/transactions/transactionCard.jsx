import { Badge, Box, Card, CardBody, CardHeader, Flex, Heading, Icon, Text } from "@chakra-ui/react";
import { useAuth } from "@clerk/clerk-react";
import axios from "axios";
import { FaRegCalendar } from "react-icons/fa6";
import CategorySelector from "../categories/categorySelector";

const TransactionCard = ({ transaction, allCategories }) => {
    const positiveColor = "#4AB74E";
    const negativeColor = "#C5594D";
    const { getToken } = useAuth();

    const handleOnChangeCategory = async (categories) => {
        const token = await getToken();
        console.log(`Categories selected: ${categories}`);
        const categoriesValues = categories.map(cat => cat.value.category_id);
        console.log(categoriesValues);
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        await axios.put(
            `http://localhost:8000/transactions/${transaction.transaction_id}/classify`,
            categoriesValues)
            .then((response) => {
                console.log(response);
            }).catch((error) => {
                console.error(error);
            });
    };

    return (
        <Card maxW='sm' margin={3}>
            <CardHeader
                justify='space-between'
                flexWrap='wrap'
                alignItems='center'
                as={Flex}
            >
                <Box as={Flex} alignItems='center'>
                    <Heading size="md" color={transaction.amount > 0 ? positiveColor : negativeColor} as={Box}>{transaction.amount} {transaction.currency}</Heading>
                    <Badge margin={2} color="#327AC0">{transaction.transaction_type}</Badge>
                </Box>
                <Text as={Box} size='sm' color='gray.500'><Icon as={FaRegCalendar} /> {transaction.booking_date}</Text>
            </CardHeader>

            <CardBody>
                <CategorySelector initialCategories={transaction.categories} allCategories={allCategories} handleOnChangeCategory={handleOnChangeCategory} />
                <Box as={Flex} justifyContent='start' flexWrap="wrap">
                </Box>
            </CardBody>
        </Card>
    );
}

export default TransactionCard;
