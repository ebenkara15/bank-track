import { Box, Center, Heading, Spinner, Text } from '@chakra-ui/react';
import { SignInButton, useUser } from '@clerk/clerk-react';
import { useBankDataContext } from '../../provider/BankDataProvider';
import { mostRecentBalance } from '../../utils/sorts';
import AccountCard from './accountCard';
import AccountRegistration from './accountRegistration';



const Accounts = () => {
    const { isSignedIn, isLoaded } = useUser();
    const { accounts, isLoading } = useBankDataContext();

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
    else if (!isSignedIn) {
        return <Box>Sign in to view your accounts  <SignInButton /></Box>;
    }
    else if (isSignedIn && !accounts) {
        return (
            <Box>
                <Text>You have no account registered. Start by adding an account: <button>Add an account</button></Text>
                <AccountRegistration />
            </Box>
        );
    }
    else {
        const sortedBalanceAccounts = accounts.map(acc => {
            return { ...acc, balances: [mostRecentBalance(acc.balances)] }
        });
        return (
            <>
                {sortedBalanceAccounts ? sortedBalanceAccounts.map(acc => (
                    <AccountCard
                        key={acc.account_id}
                        balances={acc.balances}
                        product={acc.product}
                    />
                )) : "You have no accounts yet."}
            </>
        );
    }
}

export default Accounts;
