import { useAuth } from '@clerk/clerk-react';
import axios from 'axios';
import { useEffect, useMemo, useState, } from 'react';
import Select from 'react-select';
import countryList from 'react-select-country-list';

const InstitutionSelector = () => {
    const { getToken } = useAuth();

    const countriesOptions = useMemo(() => countryList().getData(), [])
    const [country, setCountry] = useState(null);
    const [institutionsOptions, setInstitutionsOptions] = useState([]);
    const [institution, setInstitution] = useState(null);
    const [requisition, setRequisition] = useState(null);


    useEffect(() => {
        if (country) {
            fetchInstitutionsByCountry(country.value);
        }
    }, [country]); // This useEffect will run every time the 'country' state changes.

    const fetchInstitutionsByCountry = async (countryCode) => {
        console.log(`Fetching institutions for country ${countryCode}`);

        const token = await getToken(); // Ensure you await the token.

        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        axios.get(`http://localhost:8000/accounts/institutions/${countryCode}`)
            .then((response) => {
                const data = response.data;
                console.log(data);
                setInstitutionsOptions(data.map(institution => ({ value: institution.id, label: institution.name }))); // Map data for Select
            }).catch((error) => {
                console.error(error);
                // handle error, e.g., setIsError(true);
            });
    }

    const handleCountryChange = selectedOption => {
        setCountry(selectedOption);
    }
    useEffect(() => {
        if (institution) {
            fetchAgreement(institution.value);
        }
    }, [institution]); // This useEffect will run every time the 'country' state changes.


    const fetchAgreement = async (institutionId) => {
        console.log(`Creating agreement for institution ${institutionId}`);

        const token = await getToken(); // Ensure you await the token.

        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        axios.post(`http://localhost:8000/accounts/${institutionId}/agreement`)
            .then((response) => {
                const data = response.data;
                console.log(data);
                setRequisition(data);
            }).catch((error) => {
                console.error(error);
                // handle error, e.g., setIsError(true);
            });
    }

    const handleInstitutionChange = selectedOption => {
        setInstitution(selectedOption);
    }

    return (
        <>
            <label htmlFor="country">Country</label>
            <Select
                id='country'
                options={countriesOptions}
                value={country}
                onChange={handleCountryChange}
                getOptionLabel={(option) => option.label}
                getOptionValue={(option) => option.value}
            />
            {institutionsOptions.length > 0 && (
                <>
                    <label htmlFor="institution">Institution</label>
                    <Select
                        id='institution'
                        options={institutionsOptions}
                        value={institution}
                        onChange={handleInstitutionChange}
                        getOptionLabel={(option) => option.label}
                        getOptionValue={(option) => option.value}
                    />
                </>
            )}
            {requisition && (
                <a role='button' href={requisition.link} target='_blank' >Verifiy my account</a>
            )}
        </>
    );
};

export default InstitutionSelector;
