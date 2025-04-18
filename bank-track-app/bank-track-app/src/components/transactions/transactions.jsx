import {
    Center, Grid, GridItem, Heading, Spinner
} from '@chakra-ui/react';
import { useUser } from '@clerk/clerk-react';
import { useBankDataContext } from '../../provider/BankDataProvider';
import TransactionsChart from '../charts/transactionsChart';
import TransactionsList from './trasanctionsList';

const Transactions = ({ accountId = null }) => {
    const { isLoaded } = useUser();
    const { transactions, categories, isLoading } = useBankDataContext();
    // const accountIdDummy = "9db37e15-a2bf-46be-932b-0e0ec7b336f8";


    if (!isLoaded && isLoading) {
        return (
            <Center h="100vh" axis='both'>
                <Heading color="navy" size="lg" marginRight={3}>
                    Loading
                </Heading>
                <Spinner
                    thickness='4px'
                    speed='0.65s'
                    emptyColor='gray.200'
                    color='navy'
                    size='lg'
                />
            </Center>
        );
    }
    else if (transactions && categories && transactions.length > 0) {
        const transactionsByAccount = accountId ? transactions.filter(transac => transac.account.account_id === accountId) : transactions;
        return (
            <Grid
                templateAreas={`"transactions chart"
                                "transactions chart"
                                "transactions chart"`}
                templateColumns="repeat(3, 1fr)"
            >
                <GridItem
                    overflowY={'auto'}
                    maxHeight={'100vh'}
                    width={'100%'}
                    padding={1}
                    borderRight={'solid'}
                    borderRightColor={'gray.300'}
                    colSpan={1}
                    area={'transactions'}
                >
                    {transactionsByAccount ? <TransactionsList transactions={transactionsByAccount} allCategories={categories} /> : "No transactions available."}
                </GridItem>
                <GridItem
                    maxHeight={'90vh'}
                    width={'100%'}
                    padding={1}
                    colSpan={2}
                    area={'chart'}
                >
                    <TransactionsChart transactions={transactionsByAccount} id='transactionsBar' />
                </GridItem>
            </Grid>
        );
    }

};

export default Transactions;
